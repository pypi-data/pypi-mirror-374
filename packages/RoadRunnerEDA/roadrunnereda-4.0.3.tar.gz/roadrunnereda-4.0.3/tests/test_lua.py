from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from roadrunner.config import ConfigContext, ConfigLink, Location, Origin, makeConfigFromStr
from roadrunner.lua import LuaCtxt, LuaSnippet, LuaError


class TestLuaCtxt(unittest.TestCase):
    def test_simple(self):
        ctxt = LuaCtxt()
        vars = {
            "foo": "bar",
            "prime": 17,
            "link": ConfigLink("=:mod.sub", Origin(0, 0, "test"), Location(Path("."))),
        }
        ctxt.addVariables(vars)
        snip = LuaSnippet("foo", "test", 0)
        self.assertEqual(ctxt.run(snip), "bar")
        snip = LuaSnippet("prime", "test", 0)
        self.assertEqual(ctxt.run(snip), 17)
        snip = LuaSnippet("link", "test", 0)
        self.assertEqual(ctxt.run(snip), vars['link'])

    def test_inline(self):
        ctxt = LuaCtxt()
        vars = {
            "foo": "bar",
            "prime": 17,
            "float": 12.30,
            "link": ConfigLink("=:mod.sub", Origin(0, 0, "test"), Location(Path("."))),
        }
        ctxt.addVariables(vars)
        snip = LuaSnippet("foo:<%= foo %> prime:<%= prime %> float:<%-float%>", "test", 0, template=True)
        self.assertEqual(ctxt.run(snip), "foo:bar prime:17 float:12.3")

    def test_etluaError(self):
        ctxt = LuaCtxt()
        snip = LuaSnippet("something <% braak %>", "testTemplate", 0, template=True)
        self.assertRaises(LuaError, ctxt.run, snip)

    def test_coroutine(self):
        ctxt = LuaCtxt()
        source = """
          for i = 0,5 do
            coroutine.yield(i)
          end
        """
        snip = LuaSnippet(source, "test_lua.py", 43, program=True)
        fn = ctxt.compile(snip)
        cr = fn.start()
        val = []
        for i in range(6):
            val.append(cr.tick())
        self.assertListEqual(val, list(range(6)))

    def test_logging(self):
        ctxt = LuaCtxt()
        source = """
          print("Hallo Welt!")
          return 0
        """
        snip = LuaSnippet(source, "test_lua.py", 58, program=True)
        with self.assertLogs("lua") as cm:
          ctxt.run(snip)
        self.assertListEqual(cm.output, ['INFO:lua:Hallo Welt!'])

    def test_numbers(self):
        ctxt = LuaCtxt()
        source = """
          a = 15 --integer
          b = 12.0 --float
          print("integer:" .. a)
          print("float:" .. b)
          print("truediv:" .. (7//2))
          return 0
        """
        snip = LuaSnippet(source, "test_lua.py", 70, program=True)
        with self.assertLogs("lua") as cm:
          ctxt.run(snip)
        exp = [
           "INFO:lua:integer:15",
           "INFO:lua:float:12.0",
           "INFO:lua:truediv:3"
        ]
        for line in exp:
          self.assertIn(line, cm.output)

    def test_errorRuntime(self):
        ctxt = LuaCtxt()
        source = """
          a = 15

          b = "hallo"

          print(a + b)
        """
        snip = LuaSnippet(source, "test_lua.py", 86, program=True)
        fn = ctxt.compile(snip)
        with self.assertRaises(LuaError) as cm:
          fn.call()
        exp = 'LUA Error in snippet @:test_lua.py:86\ntest_lua.py:91: attempt to add a \'number\' with a \'string\'\nstack traceback:\n\ttest_lua.py:91: in function <[string "<python>"]:1>\n\t[C]: in metamethod \'add\''
        self.assertEqual(cm.exception.args[0], exp)

    def test_errorCompile(self):
        ctxt = LuaCtxt()
        source = """
          for a=1,5
          b = "hallo"
          print(a + b)
        """
        snip = LuaSnippet(source, "test_lua.py", 102, program=True)
        with self.assertRaises(LuaError) as cm:
          ctxt.compile(snip)
        exp = "LUA Error in snippet @:test_lua.py:102\nerror loading code: test_lua.py:104: 'do' expected near 'b'"
        self.assertEqual(cm.exception.args[0], exp)
        

class TestVarReplace(unittest.TestCase):
    def test_simple(self):
        rrf = """
          vars:
            foo: bar
          test: Hallo <%-foo%>
        """
        cfg = ConfigContext(makeConfigFromStr(rrf, Location("local")))
        val = cfg.get(".test")
        self.assertEqual(val, "Hallo bar")

    def test_link(self):
        rrf = """
          vars:
            link: =:mod.sub
            animal: monkey
          mod:
            sub:
              monkey: mandrill
              bird: kea
          test: =$link.bird
        """
        cfg = ConfigContext(makeConfigFromStr(rrf, Location("local")))
        self.assertEqual(cfg.get(".test"), "kea")
        self.assertEqual(cfg.get("$link.bird"), "kea")

    def test_linkLocal(self):
        rrf = """
          vars:
            link: =:foo
          mod1:
            vars:
              link: =...sub1
            sub1: monkey
            sub2: bird
          foo: bar
          test1: =$link
          test2: =:mod1$link
        """
        cfg = ConfigContext(makeConfigFromStr(rrf, Location("local")))
        #use vars defined at root
        self.assertEqual(cfg.get("$link"), "bar")
        #use vars defined in mod1
        self.assertEqual(cfg.get(".mod1$link"), "monkey")
        #use in tree links
        self.assertEqual(cfg.get(".test1"), "bar")
        self.assertEqual(cfg.get(".test2"), "monkey")

