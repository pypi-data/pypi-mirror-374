# Copyright 2024 Advanced Micro Devices, Inc
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from typing import Optional

import torch

from sharktank.layers import *
from sharktank.ops import softmax, topk, zeros_like, reshard_like
from sharktank.types import ShardedTensor, Theta

__all__ = [
    "MoeBlock",
]


class MoeBlock(ThetaLayer):
    """
    This implementation considers MoE operations as block-sparse
    operations to support imbalanced token assignments to experts.
    This enables the MoE to operate at a faster rate and in full capacity without any dropped tokens
    (or reduced performance).
    """

    def __init__(
        self,
        theta: Theta,
        rms_epsilon: float,
        moe_activation=torch.nn.functional.silu,
        *,
        experts_ffn_moe_block: PreGatherFFNMOE | DenseFFNMOE | str = "DenseFFNMOE",
        score_experts=softmax,
        normalize_experts=True,
        expert_count: Optional[int] = None,
        expert_used_count: int,
        expert_shared_count: Optional[int] = None,
        n_expert_groups: Optional[int] = None,
        n_limited_groups: Optional[int] = None,
        route_scale: Optional[float] = None,
        model_arch: Optional[str] = None,
    ):
        super().__init__(theta)
        if n_expert_groups is not None:
            if expert_count is None:
                raise ValueError(
                    "expert_count must not be None when n_expert_groups is specified."
                )
            if expert_count % n_expert_groups != 0:
                raise ValueError(
                    (
                        f"Number of experts {expert_count} must be divisible by the "
                        f"number of expert groups {n_expert_groups}."
                    )
                )
            n_experts_per_group = expert_count // n_expert_groups
            if n_limited_groups is not None and n_experts_per_group < n_limited_groups:
                raise ValueError(
                    (
                        f"Number of limited expert groups {n_limited_groups} must be at "
                        f"most the number of experts per group {n_experts_per_group}."
                    )
                )
        self.expert_used_count = expert_used_count
        self.expert_count = expert_count
        self.expert_shared_count = expert_shared_count
        self.n_expert_groups = n_expert_groups
        self.n_limited_groups = n_limited_groups
        self.score_experts = score_experts
        self.normalize_experts = normalize_experts
        self.route_scale = route_scale

        self.layer_output_norm = torch.nn.Identity()
        self.ffn_gate_inp = torch.nn.Identity()

        routed_ffn_theta = Theta(
            {
                "ffn_gate": theta("ffn_gate_exps").tree,
                "ffn_up": theta("ffn_up_exps").tree,
                "ffn_down": theta("ffn_down_exps").tree,
            }
        )

        # Add router gate
        if theta.optional_tensor("ffn_gate_inp") is not None:
            self.add_module("ffn_gate_inp", LinearLayer(theta("ffn_gate_inp")))

        # Add expert_count x FFN
        if isinstance(experts_ffn_moe_block, str):
            if experts_ffn_moe_block == "PreGatherFFNMOE":
                self.routed_experts = PreGatherFFNMOE(
                    routed_ffn_theta,
                    activation_fn=moe_activation,
                    model_arch=model_arch,
                )
            elif experts_ffn_moe_block == "DenseFFNMOE":
                self.routed_experts = DenseFFNMOE(
                    routed_ffn_theta,
                    expert_count=expert_count,
                    activation_fn=moe_activation,
                )
            else:
                raise ValueError(
                    f'Unknown experts_ffn_moe_block "{experts_ffn_moe_block}"'
                )
        else:
            self.routed_experts = experts_ffn_moe_block

        if self.expert_shared_count is not None:
            shared_ffn_theta = theta
            if theta.optional_tensor("ffn_gate_shexp") is not None:
                shared_ffn_theta = Theta(
                    {
                        "ffn_gate": theta("ffn_gate_shexp").tree,
                        "ffn_up": theta("ffn_up_shexp").tree,
                        "ffn_down": theta("ffn_down_shexp").tree,
                    }
                )
            self.shared_experts = FFN(
                theta=shared_ffn_theta,
                activation_fn=moe_activation,
            )

        # Add optional FFN output norm layer
        if theta.optional_tensor("layer_output_norm") is not None:
            self.layer_output_norm = RMSNormLayer(
                theta("layer_output_norm"), epsilon=rms_epsilon
            )

    def forward(
        self,
        # shape: (batch_size, sequence_length, feature_dim)
        h: torch.Tensor | ShardedTensor,
    ):
        batch_size, sequence_length, feature_dim = h.shape
        ffn_input = h.view(-1, feature_dim)

        # For each token, the router calculates the router weights for all experts
        # shape: (batch_size * sequence_length, expert_count)
        router_logits = self.ffn_gate_inp(ffn_input)
        router_weights = self.score_experts(router_logits.to(torch.float))

        router_weights = reshard_like(router_weights, like=ffn_input)

        # Select top k experts from router weights
        if self.n_expert_groups is not None and self.n_limited_groups is not None:
            scores_for_choice = router_weights.view(-1, self.expert_count)

            group_scores = (
                router_weights.view(
                    -1, self.n_expert_groups, self.expert_count // self.n_expert_groups
                )
                .topk(2, dim=-1)[0]
                .sum(dim=-1)
            )
            group_idx = topk(group_scores, k=self.n_limited_groups, dim=-1)[1]
            group_mask = zeros_like(group_scores)
            group_mask.scatter_(1, group_idx, 1)
            score_mask = (
                group_mask.unsqueeze(-1)
                .expand(
                    -1, self.n_expert_groups, self.expert_count // self.n_expert_groups
                )
                .reshape(-1, self.expert_count)
            )
            scores_for_choice = scores_for_choice.masked_fill(~score_mask.bool(), 0.0)
            # shape: (batch_size * sequence_length, expert_used_count)
            expert_gate, top_k_experts = topk(
                scores_for_choice, k=self.expert_used_count, dim=-1
            )
        else:
            # shape: (batch_size * sequence_length, expert_used_count)
            expert_gate, top_k_experts = topk(
                router_weights, self.expert_used_count, dim=-1
            )

        if self.normalize_experts:
            expert_gate /= expert_gate.sum(dim=-1, keepdim=True)

        expert_gate = expert_gate.to(ffn_input.dtype)

        if self.route_scale is not None:
            expert_gate = expert_gate * self.route_scale

        # shape: (batch_size * sequence_length, feature_dim)
        moe_output = self.routed_experts(ffn_input, top_k_experts, expert_gate)

        if self.expert_shared_count is not None:
            moe_output = moe_output + self.shared_experts(ffn_input)

        moe_output = moe_output.reshape(batch_size, sequence_length, feature_dim)

        moe_output = self.layer_output_norm(moe_output)

        return moe_output
