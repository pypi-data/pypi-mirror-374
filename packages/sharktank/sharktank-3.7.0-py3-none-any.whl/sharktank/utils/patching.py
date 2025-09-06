# Copyright 2024 Advanced Micro Devices, Inc.
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from pathlib import Path
from typing import Any, TYPE_CHECKING, Union
from collections.abc import Mapping, Iterable
from sharktank.types import InferenceTensor, unbox_tensor
import logging
import re
import torch

if TYPE_CHECKING:
    from sharktank.types import AnyTensor, InferenceTensor

logger = logging.getLogger(__name__)


class Patch:
    """Patches calls to forward, allowing various forms of interception."""

    def patch_child_modules(self, module: torch.nn.Module):
        """Given a network, wraps the forward() method of children.

        Different types of callbacks can be specified to control wrapping:
        * before_forward: Called with (module_name, module, args, kwarg) before
        forward function. Used for logging inputs to a module.
        * after_forward: Called with (module_name, module, results) after the
        forward function returns. Used for logging results.
        """

        def _patch(name: str, m: torch.nn.Module):
            orig_forward = m.forward

            def wrapper(*args, **kwargs):
                self.before_forward(name, m, args, kwargs)
                results = orig_forward(*args, **kwargs)
                self.after_forward(name, m, results)
                return results

            m.forward = wrapper

        for name, m in module.named_modules():
            _patch(name, m)

    def before_forward(
        self,
        module_name: str,
        module: torch.nn.Module,
        args: list[Any],
        kwargs: dict[str, Any],
    ):
        """Called before every patched forward() function."""
        pass

    def after_forward(self, module_name: str, module: torch.nn.Module, results):
        """Called after every patched forward() function with results."""
        ...


class SaveModuleResultTensorsPatch(Patch):
    """Module patch which saves the results of all modules to a safetensors file.

    Duplicate module invocations are suffixed with "#n" where n is the zero
    based call counter.

    Modules that return multiple results or non tensor results are ignored.

    Users must call finalize() once all tensors have been accumulated.
    """

    def __init__(self, with_before_forward: bool = False):
        self.with_before_forward = with_before_forward
        self.tensors: dict[str, torch.Tensor] = {}
        # Map of module_name to last used index for duplicated tensors.
        self.duplicate_tensors: dict[str, torch.Tensor] = {}

    def before_forward(
        self,
        module_name: str,
        module: torch.nn.Module,
        args: list[Any],
        kwargs: dict[str, Any],
    ):
        if not self.with_before_forward:
            return

        self._add_nested_tensors(
            name_prefix=f"{module_name}.arg", tensors=args, name_delimiter="%"
        )
        self._add_nested_tensors(
            name_prefix=f"{module_name}.arg", tensors=kwargs, name_delimiter="%"
        )

    def after_forward(self, module_name: str, module: torch.nn.Module, results: Any):
        self._add_nested_tensors(
            name_prefix=module_name, tensors=results, name_delimiter="%"
        )

    def save_file(self, output_path: Path, *, skip_unsupported_dtypes: bool = False):
        """Saves accumulated tensors to the given file.
        Args:
        skip_unsupported_dtypes:
            skip tensors with dtype that is unsupported by safetensors.
            Warn when such a tensor is encountered."""
        from safetensors.torch import save_file

        tensor_dict = self.tensors
        if skip_unsupported_dtypes:
            safetensors_unsupported_dtypes = set(
                [torch.complex32, torch.complex64, torch.complex128]
            )
            unsupported_tensor_dict = {
                k: v
                for k, v in self.tensors.items()
                if v.dtype in safetensors_unsupported_dtypes
            }
            if len(unsupported_tensor_dict) > 0:
                unsupported_dtypes = {
                    k: v.dtype for k, v in unsupported_tensor_dict.items()
                }
                logger.warning(
                    f"Safetensors could not save tensor(s) with dtype {unsupported_dtypes}"
                )
                tensor_dict = {
                    k: v
                    for k, v in tensor_dict.items()
                    if k not in unsupported_tensor_dict.keys()
                }

        save_file(tensor_dict, output_path)

    def _add_nested_tensors(
        self,
        name_prefix: str,
        tensors: list[Any] | dict[str, Any] | torch.Tensor,
        name_delimiter: str,
    ):
        if isinstance(tensors, (torch.Tensor, InferenceTensor)):
            self._add_tensor(name=name_prefix, tensor=unbox_tensor(tensors))
        elif isinstance(tensors, Mapping):
            for k, v in tensors.items():
                self._add_nested_tensors(
                    f"{name_prefix}{name_delimiter}{k}", v, name_delimiter
                )
        elif isinstance(tensors, Iterable):
            for i, v in enumerate(tensors):
                self._add_nested_tensors(
                    f"{name_prefix}{name_delimiter}{i}", v, name_delimiter
                )
        else:
            logger.warning(f"Could not handle element of type {type(tensors)}.")

    def _add_tensor(self, name: str, tensor: torch.Tensor):
        tensor = torch.detach(tensor).contiguous().to(device="cpu").clone()
        if name in self.tensors:
            orig_dup = self.tensors[name]
            del self.tensors[name]
            self.duplicate_tensors[name] = 0
            self.tensors[f"{name}#0"] = orig_dup
        if name in self.duplicate_tensors:
            index = self.duplicate_tensors[name] + 1
            self.duplicate_tensors[name] = index
            self.tensors[f"{name}#{index}"] = tensor
        else:
            self.tensors[name] = tensor


class TraceTensorModulePatch(Patch):
    """Trace tensors using the sharktank.ops.trace_tensor mechanism.

    This can be used to trace tensors both in eager and during execution with IREE.
    Usually it allows to get adequate tracing density when models are decomposed into
    multiple nested torch modules.
    """

    def __init__(
        self, with_before_forward: bool = False, exclude_regex: str | None = None
    ):
        """
        exclude_regex: exclude fully qualified trace keys that match a regex search
            with this pattern.
        """
        self.with_before_forward = with_before_forward
        self.exclude_regex = exclude_regex

    def before_forward(
        self,
        module_name: str,
        module: torch.nn.Module,
        args: list[Any],
        kwargs: dict[str, Any],
    ):
        if not self.with_before_forward:
            return

        self.trace_tensor(
            module_name=module_name,
            module=module,
            key="arg",
            args=args,
            kwargs=kwargs,
        )

    def after_forward(self, module_name: str, module: torch.nn.Module, results: Any):
        self.trace_tensor(
            module_name=module_name,
            module=module,
            key="",
            args=results,
            kwargs={},
        )

    def trace_tensor(
        self,
        module_name: str,
        module: torch.nn.Module,
        key: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ):
        from sharktank.layers import BaseLayer
        from sharktank import ops

        def _trace_if_tensor(key: str, maybe_tensor: Union["AnyTensor", Any]):
            if self.exclude_regex is not None and re.search(
                self.exclude_regex, f"{module_name}.{key}"
            ):
                return
            if not isinstance(maybe_tensor, (torch.Tensor, InferenceTensor)):
                return

            if isinstance(module, BaseLayer):
                module.trace_tensor(key, maybe_tensor)
            else:
                ops.trace_tensor(f"{module_name}.{key}", maybe_tensor)

        if isinstance(module, BaseLayer):
            for i, arg in enumerate(args):
                _trace_if_tensor(key=f"{key}%{i}", maybe_tensor=arg)
            for arg_name, arg in kwargs.items():
                _trace_if_tensor(key=f"{key}%{arg_name}", maybe_tensor=arg)
