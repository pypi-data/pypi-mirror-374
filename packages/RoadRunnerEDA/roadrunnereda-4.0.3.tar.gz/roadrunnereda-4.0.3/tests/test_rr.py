from pathlib import Path
from tempfile import TemporaryDirectory
import tempfile
import unittest

from roadrunner import rr
from roadrunner.config import ConfigContext, Location, Option, makeConfigFromStr
from roadrunner.lua import LuaSnippet


class TestQueryArgs(unittest.TestCase):
    def test_simple(self):
        cfg = ConfigContext(makeConfigFromStr("""
          _run:
            args:
              - foo
              - bar
              - --opt
              - "17"
              - --tusk
        """, Location("local")))
        with rr.QueryArgs(cfg) as args:
            args.addstr("first")
            args.addstr("second")   
            args.addflag("--flabber")
            args.addflag("--tusk")
            args.add("--opt", type=int)
        self.assertEqual(args.first, "foo")
        self.assertEqual(args.second, "bar")
        self.assertEqual(args.flabber, False)
        self.assertEqual(args.tusk, True)
        self.assertEqual(args.opt, 17)

    def test_argNotStr(self):
        cfg = ConfigContext(makeConfigFromStr("""
          _run:
            args:
              - 17
        """, Location("local")))
        with self.assertRaises(TypeError):
            with rr.QueryArgs(cfg) as args:
                args.add("first", type=int)
            self.assertEqual(args.first, 17)

class TestCall(unittest.TestCase):
    def test_simple(self):
        exp = [
          "#!env/foo.sh\n",
          "set -e\n",
          "ENV1=path1:path2:path3 \\\n",
          "braak \\\n",
          "arg1 \\\n",
          "arg2 \\\n",
          "--opt \\\n",
          "17\n",
          "\n",
          "blubber\n",
          "\n"
        ]
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            call = rr.Call(tmp, "test", "foo")
            call.addArgs(["braak", "arg1", "arg2"])
            call.addArgs(["--opt", "17"])
            call.nextCmd()
            call.addArgs(["blubber"])
            call.envSet("ENV1", "path1")
            call.envAddPaths("ENV1", [Path("path2"), Path("path3")])
            script = call.commit()
            self.assertEqual(script, Path("calls/test.sh"))
            self.assertTrue((tmp / script).exists())
            with open(tmp / script) as f:
                data = f.readlines()
            self.assertListEqual(data, exp)

    def test_version(self):
        exp = [
          "#!env/foo_vbar.sh\n",
          'braak \\\n',
          'arg1 \\\n',
          'arg2\n',
          '\n'
        ]
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            call = rr.Call(tmp, "test", "foo", "vbar")
            call.addArgs(["braak", "arg1", "arg2"])
            script = call.commit()
            self.assertEqual(script, Path("calls/test.sh"))
            self.assertTrue((tmp / script).exists())
            with open(tmp / script) as f:
                data = f.readlines()
            self.assertListEqual(data, exp)

class TestPiplineItem(unittest.TestCase):
    def test_simple(self):
        exp = {'name': 'foo'}
        pi = rr.PipelineItem("foo")
        dd = pi.render()
        self.assertDictEqual(dd, exp)

    def test_attrs(self):
        exp = {
            'name': 'foo',
            'workdir': 'wd',
            'envs': ['tool1', 'tool2'],
            'files': [('tool', 'attr', 'dest')],
            'expose': ['foo/bar:monkey', 'foo2/bar'],
            'discover': ['foo3/bar2:bird', 'foo4/bar'],
            'result': True,
            'export': [{'pattern': '*', 'base': 'baseDrum', 'dest': 'dest', 'group': 'grp1'}],
            'script': 'foo.sh',
            'abortOnError': False,
            'interactive': True,
        }
        pi = rr.PipelineItem("foo")
        pi.workdir = "wd"
        pi.tools = ['tool1', 'tool2']
        pi.links = [('tool', 'attr', 'dest')]
        pi.expose = [(Path("foo/bar"), "monkey"), (Path("foo2/bar"), None)]
        pi.discover = [(Path("foo3/bar2"), "bird"), (Path("foo4/bar"), None)]
        pi.export = [('*', Path('baseDrum'), Path('dest'), 'grp1')]
        pi.mode = rr.PipelineItem.CommandMode.CALL
        pi.call = (Path('foo.sh'), False, True)
        pi.result = True
        dd = pi.render()
        self.assertDictEqual(dd, exp)

    def test_callDefaults(self):
        exp = {
            'name': 'foo',
            'script': 'foo.sh',
        }
        pi = rr.PipelineItem("foo")
        pi.mode = rr.PipelineItem.CommandMode.CALL
        pi.call = (Path('foo.sh'), True, False)
        dd = pi.render()
        self.assertDictEqual(dd, exp)
        
    def test_exportDefaults(self):
        exp = {
            'name': 'foo',
            'export': [{'pattern': '*'}],
        }
        pi = rr.PipelineItem("foo")
        pi.export = [('*', None, None, None)]
        dd = pi.render()
        self.assertDictEqual(dd, exp)
        
class TestPipeline(unittest.TestCase):
    def test_empty(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            tmp = Path(tmpDir)
            pipe = rr.Pipeline(tmp, "emptyPipe")
            pipe.commit()
            self.assertEqual(len([x for x in tmp.iterdir()]), 0)

    def test_version(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            tmp = Path(tmpDir)
            pipe = rr.Pipeline(tmp, "versionTest")
            call = rr.Call(pipe.initWorkDir(), "call1", "hammer", "brute")
            call.addArgs(["bum", "bum"])
            pipe.addCall(call)
            exp = {'name': 'call1', 'envs': ['hammer:brute'], 'script': 'calls/call1.sh'}
            dd = pipe.root.render()
            self.assertEqual(dd['command'], exp)

class TestCommandName(unittest.TestCase):
    def test_simple(self):
        rrDef = """
          foo:
            bar:
              node: val
        """
        rcfg = ConfigContext(makeConfigFromStr(rrDef, Location("local")))
        cfg = rcfg.move(".foo.bar.node")
        nam = rr.command_name(cfg)
        self.assertEqual(nam, "foo.bar.node")

    def test_linked(self):
        rrDef = """
          foo:
            bar:
              node:
                val: braak
                options: flak
            link: =:foo.bar+flak
        """
        rcfg = ConfigContext(makeConfigFromStr(rrDef, Location("local")))
        cfg = rcfg.move(".foo.link.node")
        nam = rr.command_name(cfg)
        self.assertEqual(nam, "foo.bar.node+flak")

class TestWorkdirName(unittest.TestCase):
    rrDef = """
        _setup:
          workdir_base: cwdb
        foo:
          bar:
            node:
              val: braak
              options: theFlag
    """
    def test_simple(self):
        rcfg = ConfigContext(makeConfigFromStr(self.rrDef, Location("local")))
        cfg = rcfg.move(".foo.bar.node")
        nam = rr.workdir_name(cfg)
        self.assertEqual(nam, Path("cwdb/cmds/foo.bar.node"))

    def test_flags(self):
        rcfg = ConfigContext(makeConfigFromStr(self.rrDef, Location("local")))
        cfg = rcfg.move(".foo.bar.node", {Option('theFlag')})
        nam = rr.workdir_name(cfg)
        self.assertEqual(nam, Path("cwdb/cmds/foo.bar.node+theFlag"))

class TestWorkdir_import(unittest.TestCase):
    def test_simple(self):
        pass

class TestResultBase(unittest.TestCase):
    def test_simple(self):
        rrDef = """
          _setup:
            result_base: cwrb
        """
        rcfg = ConfigContext(makeConfigFromStr(rrDef, Location("local")))
        rb = rr.resultBase(rcfg)
        self.assertEqual(rb, Path("cwrb"))
        
class TestTemplate(unittest.TestCase):
    def test_simple(self):
        tplPath = Path("rr/rrun.py")
        filePath = Path("roadrunner/assets/rr/rrun.py")
        tpl = rr.asset(tplPath)
        with open(filePath) as f:
            expData = f.read()
        self.assertEqual(tpl.source, expData)

class TestDeployRoadExec(unittest.TestCase):
    def test_simple(self):
        with TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            rr.deployRoadExec(tmp)
            self.assertTrue((tmp / "roadexec/__init__.py").is_file())
            self.assertTrue((tmp / "psutil/__init__.py").is_file())