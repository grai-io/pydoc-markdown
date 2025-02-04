# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
This module defines the interfaces that can to be implemented for
Pydoc-Markdown to implement custom loaders for documentation data,
processors or renderers.
"""

import abc
import subprocess
import typing as t

import docspec
from databind.core import Union

if t.TYPE_CHECKING:
    from pydoc_markdown.util.docspec import ApiSuite


class Context:
    """
    Context data that is passed to plugins when they are loaded.
    """

    def __init__(self, directory: str) -> None:
        self.directory = directory


class PluginBase(abc.ABC):
    def init(self, context: Context) -> None:
        pass


# TODO(@NiklasRosenstein): Test that this works as expected.
@Union(
    [
        "!pydoc_markdown.interfaces.Loader",
        "<import>",
    ],
    style=Union.FLAT,
)
class Loader(PluginBase):
    """
    This interface describes an object that is capable of loading documentation
    data. The location from which the documentation is loaded must be defined
    with the configuration class.
    """

    @abc.abstractmethod
    def load(self) -> t.Iterable[docspec.Module]:
        ...


class LoaderError(Exception):
    pass


class Resolver(abc.ABC):
    """
    A resolver can be used by a #Processor to replace cross references with a hyperlink.
    """

    @abc.abstractmethod
    def resolve_ref(self, scope: docspec.ApiObject, ref: str) -> t.Optional[str]:
        ...


class ResolverV2(abc.ABC):
    """New style interface for resolving based on a text ref from in the context of a #docspec.ApiObject
    to find another. This is different from #Resolver because it returns the resolved object directly, instead
    of some string representation of it.
    """

    @abc.abstractmethod
    def resolve_reference(self, suite: "ApiSuite", scope: docspec.ApiObject, ref: str) -> t.Optional[docspec.ApiObject]:
        ...


# TODO(@NiklasRosenstein): Test that this works as expected.
@Union(
    [
        "!pydoc_markdown.interfaces.Processor",
        "<import>",
    ],
    style=Union.FLAT,
)
class Processor(PluginBase):
    """
    A processor is an object that takes a list of #docspec.Module#s as an input and
    transforms it in an arbitrary way. This usually processes docstrings to convert from
    various documentation syntaxes to plain Markdown.
    """

    @abc.abstractmethod
    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        ...


# TODO(@NiklasRosenstein): Test that this works as expected.
@Union(
    [
        "!pydoc_markdown.interfaces.Renderer",
        "<import>",
    ],
    style=Union.FLAT,
)
class Renderer(PluginBase):
    """
    A renderer is an object that takes a list of #docspec.Module#s as an input and produces
    output files or writes to stdout. It may also expose additional command-line arguments.
    There can only be one renderer at the end of the processor chain.

    Note that sometimes a renderer may need to perform some processing before the render step.
    To keep the possibility open that a renderer may implement generic processing that could
    used without the actual rendering functionality, #Renderer is a subclass of #Processor.
    """

    def process(self, modules: t.List[docspec.Module], resolver: t.Optional[Resolver]) -> None:
        pass

    def get_resolver(self, modules: t.List[docspec.Module]) -> t.Optional[Resolver]:
        return None

    @abc.abstractmethod
    def render(self, modules: t.List[docspec.Module]) -> None:
        ...


class SinglePageRenderer(PluginBase):
    """
    Interface for rendering a single page.
    """

    @abc.abstractmethod
    def render_single_page(
        self, fp: t.TextIO, modules: t.List[docspec.Module], page_title: t.Optional[str] = None
    ) -> None:
        ...


class SingleObjectRenderer(PluginBase):
    """
    Interface for rendering a single #docspec.ApiObject.
    """

    @abc.abstractmethod
    def render_object(self, fp: t.TextIO, obj: docspec.ApiObject, options: t.Dict[str, t.Any]) -> None:
        ...


class Server(abc.ABC):
    """
    This interface describes an object that can start a server process for
    live-viewing generated documentation in the browser. #Renderer
    implementations may additionally implement this interface to advocate their
    compatibility with the `--server` and `--open` options of the pydoc-markdown
    CLI.
    """

    @abc.abstractmethod
    def get_server_url(self) -> str:
        ...

    @abc.abstractmethod
    def start_server(self) -> subprocess.Popen:
        ...

    def reload_server(self, process: subprocess.Popen) -> subprocess.Popen:
        """
        Called when the files generated by pydoc-markdown have been updated.
        This gives the implementation a chance to reload the server process.
        The default implementation returns the *process* unchanged. Returning
        #None will automatically call #start_server() afterwards.
        """

        return process


class Builder(abc.ABC):
    """
    This interface can be implemented additionally to the #Renderer interface to
    indicate that the renderer supports building another produce after the markdown
    files have been rendered.
    """

    @abc.abstractmethod
    def build(self, site_dir: str) -> None:
        """
        Invoke the build. The *site_dir* is the directory in which the output files should be
        placed. Otherwise, the directory may be determined by the builder.
        """


# TODO(@NiklasRosenstein): Test that this works as expected.
@Union(
    [
        "!pydoc_markdown.interfaces.SourceLinker",
        "<import>",
    ],
    style=Union.FLAT,
)
class SourceLinker(PluginBase):
    """
    This interface is used to determine the URL to the source of an API object. Renderers
    can use it to place a link to the source in the generated documentation.
    """

    @abc.abstractmethod
    def get_source_url(self, obj: docspec.ApiObject) -> t.Optional[str]:
        ...
