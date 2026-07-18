import importlib.abc
import importlib.machinery
import importlib.util
import os
import platform
import shutil
import sys
import tempfile
import time
import weakref
from pathlib import Path

import pytest

from jinja2 import Environment
from jinja2 import loaders
from jinja2 import PackageLoader
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import split_template_path


class TestLoaders:
    def test_dict_loader(self, dict_loader):
        env = Environment(loader=dict_loader)
        tmpl = env.get_template("justdict.html")
        assert tmpl.render().strip() == "FOO"
        pytest.raises(TemplateNotFound, env.get_template, "missing.html")

    def test_package_loader(self, package_loader):
        env = Environment(loader=package_loader)
        tmpl = env.get_template("test.html")
        assert tmpl.render().strip() == "BAR"
        pytest.raises(TemplateNotFound, env.get_template, "missing.html")

    def test_filesystem_loader_overlapping_names(self, filesystem_loader):
        t2_dir = Path(filesystem_loader.searchpath[0]) / ".." / "templates2"
        # Make "foo" show up before "foo/test.html".
        filesystem_loader.searchpath.insert(0, t2_dir)
        e = Environment(loader=filesystem_loader)
        e.get_template("foo")
        # This would raise NotADirectoryError if "t2/foo" wasn't skipped.
        e.get_template("foo/test.html")

    def test_choice_loader(self, choice_loader):
        env = Environment(loader=choice_loader)
        tmpl = env.get_template("justdict.html")
        assert tmpl.render().strip() == "FOO"
        tmpl = env.get_template("test.html")
        assert tmpl.render().strip() == "BAR"
        pytest.raises(TemplateNotFound, env.get_template, "missing.html")

    def test_function_loader(self, function_loader):
        env = Environment(loader=function_loader)
        tmpl = env.get_template("justfunction.html")
        assert tmpl.render().strip() == "FOO"
        pytest.raises(TemplateNotFound, env.get_template, "missing.html")

    def test_prefix_loader(self, prefix_loader):
        env = Environment(loader=prefix_loader)
        tmpl = env.get_template("a/test.html")
        assert tmpl.render().strip() == "BAR"
        tmpl = env.get_template("b/justdict.html")
        assert tmpl.render().strip() == "FOO"
        pytest.raises(TemplateNotFound, env.get_template, "missing")

    def test_caching(self):
        changed = False

        class TestLoader(loaders.BaseLoader):
            def get_source(self, environment, template):
                return "foo", None, lambda: not changed

        env = Environment(loader=TestLoader(), cache_size=-1)
        tmpl = env.get_template("template")
        assert tmpl is env.get_template("template")
        changed = True
        assert tmpl is not env.get_template("template")
        changed = False

    def test_no_cache(self):
        mapping = {"foo": "one"}
        env = Environment(loader=loaders.DictLoader(mapping), cache_size=0)
        assert env.get_template("foo") is not env.get_template("foo")

    def test_limited_size_cache(self):
        mapping = {"one": "foo", "two": "bar", "three": "baz"}
        loader = loaders.DictLoader(mapping)
        env = Environment(loader=loader, cache_size=2)
        t1 = env.get_template("one")
        t2 = env.get_template("two")
        assert t2 is env.get_template("two")
        assert t1 is env.get_template("one")
        env.get_template("three")
        loader_ref = weakref.ref(loader)
        assert (loader_ref, "one") in env.cache
        assert (loader_ref, "two") not in env.cache
        assert (loader_ref, "three") in env.cache

    def test_cache_loader_change(self):
        loader1 = loaders.DictLoader({"foo": "one"})
        loader2 = loaders.DictLoader({"foo": "two"})
        env = Environment(loader=loader1, cache_size=2)
        assert env.get_template("foo").render() == "one"
        env.loader = loader2
        assert env.get_template("foo").render() == "two"

    def test_dict_loader_cache_invalidates(self):
        mapping = {"foo": "one"}
        env = Environment(loader=loaders.DictLoader(mapping))
        assert env.get_template("foo").render() == "one"
        mapping["foo"] = "two"
        assert env.get_template("foo").render() == "two"

    def test_split_template_path(self):
        assert split_template_path("foo/bar") == ["foo", "bar"]
        assert split_template_path("./foo/bar") == ["foo", "bar"]
        pytest.raises(TemplateNotFound, split_template_path, "../foo")


class TestFileSystemLoader:
    searchpath = (Path(__file__) / ".." / "res" / "templates").resolve()

    @staticmethod
    def _test_common(env):
        tmpl = env.get_template("test.html")
        assert tmpl.render().strip() == "BAR"
        tmpl = env.get_template("foo/test.html")
        assert tmpl.render().strip() == "FOO"
        pytest.raises(TemplateNotFound, env.get_template, "missing.html")

    def test_searchpath_as_str(self):
        filesystem_loader = loaders.FileSystemLoader(str(self.searchpath))

        env = Environment(loader=filesystem_loader)
        self._test_common(env)

    def test_searchpath_as_pathlib(self):
        filesystem_loader = loaders.FileSystemLoader(self.searchpath)
        env = Environment(loader=filesystem_loader)
        self._test_common(env)

    def test_searchpath_as_list_including_pathlib(self):
        filesystem_loader = loaders.FileSystemLoader(
            ["/tmp/templates", self.searchpath]
        )
        env = Environment(loader=filesystem_loader)
        self._test_common(env)

    def test_caches_template_based_on_mtime(self):
        filesystem_loader = loaders.FileSystemLoader(self.searchpath)

        env = Environment(loader=filesystem_loader)
        tmpl1 = env.get_template("test.html")
        tmpl2 = env.get_template("test.html")
        assert tmpl1 is tmpl2

        os.utime(self.searchpath / "test.html", (time.time(), time.time()))
        tmpl3 = env.get_template("test.html")
        assert tmpl1 is not tmpl3

    @pytest.mark.parametrize(
        ("encoding", "expect"),
        [
            ("utf-8", "文字化け"),
            ("iso-8859-1", "æ\x96\x87\xe5\xad\x97\xe5\x8c\x96\xe3\x81\x91"),
        ],
    )
    def test_uses_specified_encoding(self, encoding, expect):
        loader = loaders.FileSystemLoader(self.searchpath, encoding=encoding)
        e = Environment(loader=loader)
        t = e.get_template("mojibake.txt")
        assert t.render() == expect


class TestModuleLoader:
    archive = None

    def compile_down(self, prefix_loader, zip="deflated"):
        log = []
        self.reg_env = Environment(loader=prefix_loader)
        if zip is not None:
            fd, self.archive = tempfile.mkstemp(suffix=".zip")
            os.close(fd)
        else:
            self.archive = tempfile.mkdtemp()
        self.reg_env.compile_templates(self.archive, zip=zip, log_function=log.append)
        self.mod_env = Environment(loader=loaders.ModuleLoader(self.archive))
        return "".join(log)

    def teardown(self):
        if hasattr(self, "mod_env"):
            if os.path.isfile(self.archive):
                os.remove(self.archive)
            else:
                shutil.rmtree(self.archive)
            self.archive = None

    def test_log(self, prefix_loader):
        log = self.compile_down(prefix_loader)
        assert (
            'Compiled "a/foo/test.html" as '
            "tmpl_a790caf9d669e39ea4d280d597ec891c4ef0404a" in log
        )
        assert "Finished compiling templates" in log
        assert (
            'Could not compile "a/syntaxerror.html": '
            "Encountered unknown tag 'endif'" in log
        )

    def _test_common(self):
        tmpl1 = self.reg_env.get_template("a/test.html")
        tmpl2 = self.mod_env.get_template("a/test.html")
        assert tmpl1.render() == tmpl2.render()

        tmpl1 = self.reg_env.get_template("b/justdict.html")
        tmpl2 = self.mod_env.get_template("b/justdict.html")
        assert tmpl1.render() == tmpl2.render()

    def test_deflated_zip_compile(self, prefix_loader):
        self.compile_down(prefix_loader, zip="deflated")
        self._test_common()

    def test_stored_zip_compile(self, prefix_loader):
        self.compile_down(prefix_loader, zip="stored")
        self._test_common()

    def test_filesystem_compile(self, prefix_loader):
        self.compile_down(prefix_loader, zip=None)
        self._test_common()

    def test_weak_references(self, prefix_loader):
        self.compile_down(prefix_loader)
        self.mod_env.get_template("a/test.html")
        key = loaders.ModuleLoader.get_template_key("a/test.html")
        name = self.mod_env.loader.module.__name__

        assert hasattr(self.mod_env.loader.module, key)
        assert name in sys.modules

        # unset all, ensure the module is gone from sys.modules
        self.mod_env = None

        try:
            import gc

            gc.collect()
        except BaseException:
            pass

        assert name not in sys.modules

    def test_choice_loader(self, prefix_loader):
        self.compile_down(prefix_loader)
        self.mod_env.loader = loaders.ChoiceLoader(
            [self.mod_env.loader, loaders.DictLoader({"DICT_SOURCE": "DICT_TEMPLATE"})]
        )
        tmpl1 = self.mod_env.get_template("a/test.html")
        assert tmpl1.render() == "BAR"
        tmpl2 = self.mod_env.get_template("DICT_SOURCE")
        assert tmpl2.render() == "DICT_TEMPLATE"

    def test_prefix_loader(self, prefix_loader):
        self.compile_down(prefix_loader)
        self.mod_env.loader = loaders.PrefixLoader(
            {
                "MOD": self.mod_env.loader,
                "DICT": loaders.DictLoader({"test.html": "DICT_TEMPLATE"}),
            }
        )
        tmpl1 = self.mod_env.get_template("MOD/a/test.html")
        assert tmpl1.render() == "BAR"
        tmpl2 = self.mod_env.get_template("DICT/test.html")
        assert tmpl2.render() == "DICT_TEMPLATE"

    def test_path_as_pathlib(self, prefix_loader):
        self.compile_down(prefix_loader)

        mod_path = self.mod_env.loader.module.__path__[0]
        mod_loader = loaders.ModuleLoader(Path(mod_path))
        self.mod_env = Environment(loader=mod_loader)

        self._test_common()

    def test_supports_pathlib_in_list_of_paths(self, prefix_loader):
        self.compile_down(prefix_loader)

        mod_path = self.mod_env.loader.module.__path__[0]
        mod_loader = loaders.ModuleLoader([Path(mod_path), "/tmp/templates"])
        self.mod_env = Environment(loader=mod_loader)

        self._test_common()


@pytest.fixture()
def package_dir_loader(monkeypatch):
    monkeypatch.syspath_prepend(Path(__file__).parent)
    return PackageLoader("res")


@pytest.mark.parametrize(
    ("template", "expect"), [("foo/test.html", "FOO"), ("test.html", "BAR")]
)
def test_package_dir_source(package_dir_loader, template, expect):
    source, name, up_to_date = package_dir_loader.get_source(None, template)
    assert source.rstrip() == expect
    assert name.endswith(os.path.join(*split_template_path(template)))
    assert up_to_date()


def test_package_dir_list(package_dir_loader):
    templates = package_dir_loader.list_templates()
    assert "foo/test.html" in templates
    assert "test.html" in templates


@pytest.fixture()
def package_file_loader(monkeypatch):
    monkeypatch.syspath_prepend(Path(__file__).parent / "res")
    return PackageLoader("__init__")


@pytest.mark.parametrize(
    ("template", "expect"), [("foo/test.html", "FOO"), ("test.html", "BAR")]
)
def test_package_file_source(package_file_loader, template, expect):
    source, name, up_to_date = package_file_loader.get_source(None, template)
    assert source.rstrip() == expect
    assert name.endswith(os.path.join(*split_template_path(template)))
    assert up_to_date()


def test_package_file_list(package_file_loader):
    templates = package_file_loader.list_templates()
    assert "foo/test.html" in templates
    assert "test.html" in templates


@pytest.fixture()
def package_zip_loader(monkeypatch):
    package_zip = (Path(__file__) / ".." / "res" / "package.zip").resolve()
    monkeypatch.syspath_prepend(package_zip)
    return PackageLoader("t_pack")


@pytest.mark.parametrize(
    ("template", "expect"), [("foo/test.html", "FOO"), ("test.html", "BAR")]
)
def test_package_zip_source(package_zip_loader, template, expect):
    source, name, up_to_date = package_zip_loader.get_source(None, template)
    assert source.rstrip() == expect
    assert name.endswith(os.path.join(*split_template_path(template)))
    assert up_to_date is None


@pytest.mark.xfail(
    platform.python_implementation() == "PyPy",
    reason="PyPy's zipimporter doesn't have a '_files' attribute.",
    raises=TypeError,
)
def test_package_zip_list(package_zip_loader):
    assert package_zip_loader.list_templates() == ["foo/test.html", "test.html"]


@pytest.mark.parametrize("package_path", ["", ".", "./"])
def test_package_zip_omit_curdir(package_zip_loader, package_path):
    """PackageLoader should not add or include "." or "./" in the root
    path, it is invalid in zip paths.
    """
    loader = PackageLoader("t_pack", package_path)
    assert loader.package_path == ""
    source, _, _ = loader.get_source(None, "templates/foo/test.html")
    assert source.rstrip() == "FOO"


def test_pep_451_import_hook():
    class ImportHook(importlib.abc.MetaPathFinder, importlib.abc.Loader):
        def find_spec(self, name, path=None, target=None):
            if name != "res":
                return None

            spec = importlib.machinery.PathFinder.find_spec(name)
            return importlib.util.spec_from_file_location(
                name,
                spec.origin,
                loader=self,
                submodule_search_locations=spec.submodule_search_locations,
            )

        def create_module(self, spec):
            return None  # default behaviour is fine

        def exec_module(self, module):
            return None  # we need this to satisfy the interface, it's wrong

    # ensure we restore `sys.meta_path` after putting in our loader
    before = sys.meta_path[:]

    try:
        sys.meta_path.insert(0, ImportHook())
        package_loader = PackageLoader("res")
        assert "test.html" in package_loader.list_templates()
    finally:
        sys.meta_path[:] = before


class TestPathTransformation:
    """Test path transformation functionality across different loaders."""

    def test_filesystem_loader_path_transform(self):
        """Test path transformation with FileSystemLoader."""
        searchpath = (Path(__file__) / ".." / "res" / "templates").resolve()

        def transform_path(template):
            # Transform "alias.html" to "test.html"
            if template == "alias.html":
                return "test.html"
            return template

        loader = loaders.FileSystemLoader(searchpath, path_transform=transform_path)
        env = Environment(loader=loader)

        # Should load test.html when requesting alias.html
        tmpl = env.get_template("alias.html")
        assert tmpl.render().strip() == "BAR"

        # Normal templates should still work
        tmpl = env.get_template("test.html")
        assert tmpl.render().strip() == "BAR"

    def test_dict_loader_path_transform(self):
        """Test path transformation with DictLoader."""
        def transform_path(template):
            # Add .html extension if missing
            if not template.endswith('.html'):
                return template + '.html'
            return template

        mapping = {'index.html': 'Hello World', 'about.html': 'About Page'}
        loader = loaders.DictLoader(mapping, path_transform=transform_path)
        env = Environment(loader=loader)

        # Should find index.html when requesting index
        tmpl = env.get_template("index")
        assert tmpl.render() == "Hello World"

        # Should find about.html when requesting about
        tmpl = env.get_template("about")
        assert tmpl.render() == "About Page"

        # Normal templates should still work
        tmpl = env.get_template("index.html")
        assert tmpl.render() == "Hello World"

    def test_function_loader_path_transform(self):
        """Test path transformation with FunctionLoader."""
        def load_template(name):
            templates = {
                'home.html': 'Home Page',
                'contact.html': 'Contact Us'
            }
            return templates.get(name)

        def transform_path(template):
            # Convert underscore to dash
            return template.replace('_', '-')

        loader = loaders.FunctionLoader(load_template, path_transform=transform_path)
        env = Environment(loader=loader)

        # Should transform home_page.html to home-page.html, but since that doesn't exist,
        # let's test a simpler case
        def load_template_simple(name):
            if name == 'page-one.html':
                return 'Page One Content'
            return None

        loader = loaders.FunctionLoader(load_template_simple, path_transform=transform_path)
        env = Environment(loader=loader)

        # Should transform page_one.html to page-one.html
        tmpl = env.get_template("page_one.html")
        assert tmpl.render() == "Page One Content"

    def test_path_transform_with_invalid_input(self):
        """Test path transformation with invalid inputs."""
        def bad_transform(template):
            if template == "error":
                raise ValueError("Transform error")
            return template

        loader = loaders.DictLoader({'test.html': 'content'}, path_transform=bad_transform)
        env = Environment(loader=loader)

        # Should raise the transform error
        with pytest.raises(ValueError, match="Transform error"):
            env.get_template("error")

    def test_path_transform_none_handling(self):
        """Test that None path_transform works correctly."""
        loader = loaders.DictLoader({'test.html': 'content'}, path_transform=None)
        env = Environment(loader=loader)

        tmpl = env.get_template("test.html")
        assert tmpl.render() == "content"

    def test_path_transform_empty_string(self):
        """Test path transformation with empty string."""
        def transform_path(template):
            if template == "":
                return "default.html"
            return template

        loader = loaders.DictLoader({'default.html': 'default content'}, path_transform=transform_path)
        env = Environment(loader=loader)

        tmpl = env.get_template("")
        assert tmpl.render() == "default content"

    def test_path_transform_normalization(self):
        """Test path normalization through transformation."""
        def normalize_path(template):
            # Remove leading slashes and normalize separators
            template = template.lstrip('/')
            return template.replace('\\', '/')

        loader = loaders.DictLoader({
            'templates/page.html': 'normalized content'
        }, path_transform=normalize_path)
        env = Environment(loader=loader)

        # Should normalize /templates/page.html to templates/page.html
        tmpl = env.get_template("/templates/page.html")
        assert tmpl.render() == "normalized content"

    def test_path_transform_aliasing(self):
        """Test template aliasing through path transformation."""
        aliases = {
            'home': 'index.html',
            'contact': 'contact-us.html',
            'about': 'about-us.html'
        }

        def alias_transform(template):
            return aliases.get(template, template)

        templates = {
            'index.html': 'Home Page',
            'contact-us.html': 'Contact Us',
            'about-us.html': 'About Us'
        }

        loader = loaders.DictLoader(templates, path_transform=alias_transform)
        env = Environment(loader=loader)

        # Test aliases
        assert env.get_template("home").render() == "Home Page"
        assert env.get_template("contact").render() == "Contact Us"
        assert env.get_template("about").render() == "About Us"

        # Test original names still work
        assert env.get_template("index.html").render() == "Home Page"

    def test_path_transform_with_complex_logic(self):
        """Test path transformation with complex business logic."""
        def complex_transform(template):
            # Simulate version-based template selection
            if template.startswith('v2/'):
                return template[3:]  # Remove v2/ prefix
            elif template.startswith('mobile/'):
                return template.replace('mobile/', 'm-')
            elif template.endswith('.tpl'):
                return template.replace('.tpl', '.html')
            return template

        templates = {
            'page.html': 'Desktop Version',
            'm-page.html': 'Mobile Version',
            'form.html': 'Form Template'
        }

        loader = loaders.DictLoader(templates, path_transform=complex_transform)
        env = Environment(loader=loader)

        # Test v2/ prefix removal
        assert env.get_template("v2/page.html").render() == "Desktop Version"

        # Test mobile/ to m- transformation
        assert env.get_template("mobile/page.html").render() == "Mobile Version"

        # Test .tpl to .html transformation
        assert env.get_template("form.tpl").render() == "Form Template"
