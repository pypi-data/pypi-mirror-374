#!/usr/bin/env python3

import tempfile
import unittest
import pathlib
from roadrunner import lua
import roadrunner.config as config

class TestMakeConfigVal(unittest.TestCase):
    def test_simpleValues(self):
        self.assertIsInstance(config.makeConfigVal(17),     config.ConfigLeaf)
        self.assertIsInstance(config.makeConfigVal(True),   config.ConfigLeaf)
        self.assertIsInstance(config.makeConfigVal(""),     config.ConfigLeaf)
        self.assertIsInstance(config.makeConfigVal("Hallo"),config.ConfigLeaf)
        self.assertIsInstance(config.makeConfigVal("=:hallo"),config.ConfigLink)
        self.assertIsInstance(config.makeConfigVal("$hallo"),config.ConfigScript)
        self.assertIsInstance(config.makeConfigVal("+hallo"),config.ConfigImport)
        self.assertIsInstance(config.makeConfigVal({"key":"hallo"}),config.ConfigDict)
        self.assertIsInstance(config.makeConfigVal({"/key":"hallo"}),config.ConfigCond)
        self.assertIsInstance(config.makeConfigVal(["hallo", "welt"]),config.ConfigList)

    def test_emptylist(self):
        """Test empty lists loaded from string"""
        node = config.makeConfigVal([])
        env = config.ConfigEnv()
        self.assertEqual(node.getValue(env), [])


    #TODO check ConfigXXX as input value
    #TODO test to check that given a ConfigLink for example the resulting ConfigLink is equal

#TODO TestSafeLineLoader
#TODO TestMakeConfigFromFile
#TODO TestMakeConfigFromStr
#TODO TestMakeConfigFromManifest
#TODO TestWriteConfigToFile
#TODO TestWriteConfigToStr

class TestNoValue(unittest.TestCase):
    def test(self):
        nv = config.NoValue()
        self.assertIsNot(nv, None)
        self.assertIsNot(nv, bool)
        self.assertIsNot(nv, int)

class TestConfigEnv(unittest.TestCase):
    def test_init(self):
        env = config.ConfigEnv()
        self.assertIsInstance(env, config.ConfigEnv)

    def test_derive_simple(self):
        rootEnv = config.ConfigEnv()
        # basic derive
        newEnv = rootEnv.derive(("devTest",))
        self.assertEqual(newEnv.pred, rootEnv)
        self.assertEqual(newEnv.operation, ('devTest', ))
        self.assertEqual(newEnv.hist, config.ConfigPath(''))
        self.assertEqual(newEnv.flags, {})

    def test_derive_flags(self):
        rootEnv = config.ConfigEnv()
        # add flags
        newEnv = rootEnv.derive(("devTestAddFlags",), addFlags={config.Option('myFlag'), config.Option('otherFlag')})
        self.assertEqual(newEnv.flags, {'myFlag': config.Option('myFlag'), 'otherFlag': config.Option('otherFlag')})
        # remove/add flags
        newEnv2 = newEnv.derive(("devTestRemFlags",), addFlags={config.Option('third')}, remFlags={'otherFlag'})
        self.assertEqual(newEnv2.flags, {'myFlag': config.Option('myFlag'), 'third': config.Option('third')})
    
    def test_derive_move(self):
        rootEnv = config.ConfigEnv()
        # move
        newEnv = rootEnv.derive(("devTestMove", ":"), move=config.ConfigPath(':'))
        self.assertEqual(newEnv.hist, config.ConfigPath(':'))
        # relative move
        newEnv2 = newEnv.derive(("devTestMove2", ".blubber.baz"), move=config.ConfigPath('.blubber.buz'))
        self.assertEqual(newEnv2.hist, config.ConfigPath(':blubber.buz'))
        # relative move up
        newEnv3 = newEnv2.derive(("devTestMove3", "..bar"), move=config.ConfigPath('..bar'))
        self.assertEqual(newEnv3.hist, config.ConfigPath(':blubber.buz..bar'))

    def test_dump(self):
        rootEnv = config.ConfigEnv()
        env = rootEnv.derive(("step1", ":blubber"), move=config.ConfigPath(':blubber'))
        env = env.derive(("step2", "+myflag"), addFlags={config.Option('myflag')})
        lst = env.dump()
        self.assertEqual(lst, [
            'ConfigEnv(:blubber,myflag) - trace:',
            '  @:blubber                                 - step2 +myflag',
            '  @:blubber                                 - step1 :blubber',
            '  @                                         - Env'
        ])

class TestConfigNode(unittest.TestCase):
    def setUp(self):
        self.parent = config.ConfigNode()
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.node = config.ConfigNode(None, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigNode
        self.value = Exception

    def test_create(self):
        self.assertEqual(self.node.location, self.loc)
        self.assertEqual(self.node.origin, self.ori)
        self.assertEqual(self.node.parent, self.parent)
        self.assertEqual(self.node.key, "key")

    def test_clone(self):
        node = self.node.clone()
        self.assertEqual(node.location, self.loc)
        self.assertEqual(node.origin, self.ori)
        self.assertEqual(node.parent, self.parent)
        self.assertEqual(node.key, "key")
        self.assertIsInstance(node, self.cls)

        loc = config.Location("bla")
        node2 = self.node.clone(location=loc)
        self.assertEqual(node2.location, loc)
        self.assertEqual(node2.origin, self.ori)

        ori = config.Origin(15, 87)
        node3 = self.node.clone(origin=ori)
        self.assertEqual(node3.location, self.loc)
        self.assertEqual(node3.origin, ori)

    def test_items(self):
        with self.assertRaises(config.NotIteratable):
            for _ in self.node.items(self.env):
                pass

    def test_delegate(self):
        self.assertEqual(self.node.delegate(self.env), (None,None))

    def test_getId(self):
        self.assertEqual(self.node.getId(), id(self.node))

    def test_getRoot(self):
        self.assertEqual(self.node.getRoot(file=False), self.parent)
        self.assertEqual(self.node.getRoot(file=True), self.parent)

    def test_getChild(self):
        with self.assertRaises(config.ChildError):
            self.node.getChild("key", self.env)

    def test_setChild(self):
        with self.assertRaises(config.ChildError):
            self.node.setChild("key", config.ConfigNode(), self.env)
    
    def test_getValue(self):
        if self.value is Exception:
            with self.assertRaises(config.BadValue):
                self.node.getValue(self.env)
        else:
            self.assertEqual(self.node.getValue(self.env), self.value)
    
    def test_merge_over(self):
        with self.assertRaises(config.BadValue):
            self.node.merge(config.ConfigNode(), self.env, overwrite=True)

    def test_merge_under(self):
        with self.assertRaises(config.BadValue):
            self.node.merge(config.ConfigNode(), self.env, overwrite=False)

    def test_getLocation(self):
        self.assertEqual(self.node.getLocation(self.env), self.loc)
    
    def test_setParent(self):
        node = config.ConfigNode()
        self.node.setParent(node, "other")
        self.assertEqual(self.node.parent, node)
        self.assertEqual(self.node.key, "other")

    def test_getPath(self):
        self.assertEqual(self.node.getPath(), config.ConfigPath(".key"))

    def test_getLua(self):
        self.assertIsInstance(self.node.getLua(self.env), lua.LuaCtxt)

    def test_getVars(self):
        self.assertEqual(self.node.getVars(), {})

    def test_repr(self):
        self.assertEqual(self.node.__repr__(), f"{self.cls.NAME}({id(self.node)})")

    def test_dump(self):
        self.assertEqual(self.node.dump(), (self.cls.NAME, []))
        
    def test_export(self):
        if self.value is Exception:
            with self.assertRaises(Exception):
                self.node.export()
        else:
            self.assertEqual(self.node.export(), self.value)

class TestConfigLeaf(TestConfigNode):
    def setUp(self):
        self.parent = config.ConfigNode()
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.value = 18
        self.node = config.ConfigLeaf(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigLeaf

    def test_merge_under(self):
        self.node.merge(config.ConfigLeaf(32), self.env, overwrite=False)
        self.assertEqual(self.node.getValue(self.env), self.value)

    def test_merge_over(self):
        self.node.merge(config.ConfigLeaf(32), self.env, overwrite=True)
        self.assertEqual(self.node.getValue(self.env), 32)
    
    def test_repr(self):
        self.assertEqual(self.node.__repr__(), f"{self.cls.NAME}({self.value})")

    def test_dump(self):
        self.assertEqual(self.node.dump(), (str(self.value), []))

    def test_resolve(self):
        """variable resolver"""
        d1 = {
            "vars": {
                "monkey": "man<%-tool%>",
                "bird": "kea",
                "tool": "drill"
            },
            "node": {
                "vars": {
                    "dog": "labrador",
                    "bird": "pidgeon",
                    "fish": "<%-tool%> head shark",
                    "tool": "hammer"
                },
                "key1": "<%-bird%>",
                "key2": "<%-monkey%>",
                "key3": "<%-dog%>",
                "key4": "<%-fish%>"
            },
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(cnf.get(':node.key1'), "pidgeon")
        self.assertEqual(cnf.get(':node.key2'), "mandrill")
        self.assertEqual(cnf.get(':node.key3'), "labrador")
        self.assertEqual(cnf.get(':node.key4'), "hammer head shark")

    def test_resolve_reverse(self):
        """variable resolver with backwards varibales"""
        d1 = {
            "vars": {
                "animal": "kea",
                "monkey": "chimpanzee"
            },
            "node": {
                "vars": {
                    "animal": "pigeon",
                    "?monkey": "oran-utan",
                    "?bird": "parrot"
                },
                "msg": "this is a <%-animal%>",
                "msg2": "this is a <%-monkey%>",
                "msg3": "this is a <%-bird%>"
            }
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(cnf.get(":node.msg"), "this is a pigeon")
        self.assertEqual(cnf.get(":node.msg2"), "this is a chimpanzee")
        self.assertEqual(cnf.get(":node.msg3"), "this is a parrot")

    def test_location_relpath(self):
        """relpath resolver"""
        d1 = {
            "node": {
                "key1": "funky"
            },
        }
        cnf = config.makeConfigVal(d1, location=config.Location("foo"))
        self.assertEqual(
            config.ConfigContext(cnf).get(':node.key1', isOsPath=True),
            (config.Location('foo'), pathlib.Path("funky"))
        )

    def test_origin(self):
        """testing the origin system"""
        src = """
        foo:
          monkey: mandrill
          bird: kea
        """
        cnf = config.makeConfigFromStr(src, None)
        env = config.ConfigEnv()
        _, node = config.ConfigPath(".foo.monkey").follow(env, cnf)
        self.assertEqual(node.origin, config.Origin(3, 10, "<unicode string>"))

    def test_location(self):
        """testing the location system"""
        src = """
        foo:
          monkey: mandrill
          bird: kea
        """
        src2 = """
        bar:
          tool: drill
          car: mazda
        """
        cnf = config.makeConfigFromStr(src, config.Location("foo"))
        cnf2 = config.makeConfigFromStr(src2, config.Location("bar"))
        cnf.merge(cnf2, config.ConfigEnv())
        env = config.ConfigEnv()
        _, node = config.ConfigPath(".foo.monkey").follow(env, cnf)
        _, node2 = config.ConfigPath(".bar.car").follow(env, cnf)
        self.assertEqual(node.getLocation(env), config.Location("foo"))
        self.assertEqual(node2.getLocation(env), config.Location("bar"))
        self.assertEqual(node.getLocation(env), config.Location("foo"))

    def test_script(self):
        """testing script nodes"""
        d1 = {
            "mod1": {
                "inline": "Ich habe <%-5+5%> Finger",
                "eval": '$"Ich habe " .. (5+5) .. " Finger"',
                "program": '$$return "Ich habe " .. (5+5) .. " Finger"'
            }
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(cnf.get(':mod1.inline'), 'Ich habe 10 Finger')
        self.assertEqual(cnf.get(':mod1.eval'), 'Ich habe 10 Finger')
        self.assertEqual(cnf.get(':mod1.program'), 'Ich habe 10 Finger')

    def test_ospath_getter(self):
        src = """
          core:
            c:
              /VPI: [vpi/SiCoCore.c]
              /DPI: [dpi/SiCoCore.c]
              /true: [cpp/SiCo.cc]
            sv:
              /DPI: dpi/SiCoCore.sv
              /true: ""
            path:
              /C: cpp
              /true: []
            pymod: python/SiCo
        """
        cfg = config.ConfigContext(config.makeConfigFromStr(src, location=config.Location(pathlib.Path("."))))
        scfg = cfg.move(addFlags={config.Option('DPI')})
        files = scfg.get(".core.sv", isOsPath=True, mkList=True)
        self.assertEqual(files, [(config.Location(pathlib.Path(".")), pathlib.Path("dpi/SiCoCore.sv"))])



class TestConfigList(TestConfigNode):
    def setUp(self):
        self.parent = config.ConfigNode()
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.value = [13, 56, 123]
        self.node = config.ConfigList(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigList

    def test_dump(self):
        lines =  [f"- {x}" for x in self.value]
        self.assertEqual(self.node.dump(), ("", lines))

    def test_repr(self):
        self.assertEqual(self.node.__repr__(), f"{self.cls.NAME}(len:{len(self.node)})")

    def test_items(self):
        for num,tup in enumerate(self.node.items(self.env)):
            idx, env, child = tup
            self.assertEqual(idx, str(num))
            self.assertEqual(child.getValue(self.env), self.value[num])

    def test_getChild(self):
        env, node = self.node.getChild("1", self.env)
        self.assertEqual(node.getValue(env), self.value[1])

    def test_setChild(self):
        self.node.setChild("1", config.makeConfigVal(17), self.env)
        env, node = self.node.getChild("1", self.env)
        self.assertEqual(node.getValue(env), 17)
        
    def test_merge_over(self):
        with self.assertRaises(config.UnsupportedError):
            self.node.merge(config.ConfigList([12, 86]), self.env, overwrite=True)

    def test_merge_under(self):
        self.node.merge(config.ConfigList([12, 86]), self.env)
        self.assertEqual(self.node.getValue(self.env), self.value + [12, 86])

class TestConfigDict(TestConfigNode):
    def setUp(self):
        self.parent = config.ConfigNode()
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.value = {"bla": 13, "baz": 56, "foo": 123}
        self.node = config.ConfigDict(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigDict

    def test_repr(self):
        self.assertEqual(self.node.__repr__(), f"{str(self.cls.NAME)}(size:{len(self.value)})")

    def test_items(self):
        for tup in self.node.items(self.env):
            key, env, child = tup
            self.assertTrue(key in self.value)
            self.assertEqual(child.getValue(self.env), self.value[key])

    def test_getChild(self):
        env, node = self.node.getChild("baz", self.env)
        self.assertEqual(node.getValue(env), self.value["baz"])
        with self.assertRaises(config.PathNotExist):
            self.node.getChild("braak", self.env)

    def test_setChild(self):
        newChild = config.makeConfigVal("monkey")
        self.node.setChild("burbel", newChild, self.env)
        env, node = self.node.getChild("burbel", self.env)
        self.assertEqual(node.getValue(env), "monkey")

    def test_merge_over(self):
        newDict = config.makeConfigVal({"bird": "kea", "foo": 67})
        self.node.merge(newDict, self.env, overwrite=True)
        env, node = self.node.getChild("foo", self.env)
        self.assertEqual(node.getValue(env), 67)
        env, node = self.node.getChild("bla", self.env)
        self.assertEqual(node.getValue(env), 13)

    def test_merge_under(self):
        newDict = config.makeConfigVal({"bird": "kea", "foo": 67})
        self.node.merge(newDict, self.env, overwrite=False)
        env, node = self.node.getChild("foo", self.env)
        self.assertEqual(node.getValue(env), 123)
        env, node = self.node.getChild("bird", self.env)
        self.assertEqual(node.getValue(env), "kea")

    def test_dump(self):
        lines = [f"{x}: {y}" for x,y in self.value.items()]
        self.assertEqual(self.node.dump(), ("", lines))

class TestConfigCond(TestConfigNode):
    def setUp(self):
        self.parent = config.ConfigNode()
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.value = {"/bla": 13, "/baz": 56, "/default": 123}
        self.node = config.ConfigCond(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigCond

    def test_delegate(self):
        nenv, nnode = self.node.delegate(self.env)
        self.assertEqual(nnode.getValue(nenv), 123)

    def test_getValue(self):
        self.assertEqual(self.node.getValue(self.env), 123)

    # merging doesn't do anything
    def test_merge_over(self):
        self.node.merge(config.ConfigLeaf(34), self.env, overwrite=True)
        self.assertEqual(self.node.getValue(self.env), 123)

    def test_merge_under(self):
        self.node.merge(config.ConfigLeaf(34), self.env, overwrite=False)
        self.assertEqual(self.node.getValue(self.env), 123)

    def test_repr(self):
        self.assertEqual(self.node.__repr__(), f"{self.cls.NAME}()")

    def test_dump(self):
        lines = [f"{x}: {y}" for x,y in self.value.items()]
        self.assertEqual(self.node.dump(), ("", lines))

    def test_condition(self):
        """testing the condition node"""
        d1 = {
            "vars": {
                "foo": 1,
                "animal": "monkey"
            },
            "thing": {
                "/foo": "bar",
                "/true": "NA"
            },
            "other":{
                "/nothing": "noop",
                "/default": "value"
            },
            "another": {
                "/true": "<%-animal%>"
            }
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(cnf.get(':thing'), "bar")
        self.assertEqual(cnf.get(':other'), "value")
        self.assertEqual(cnf.get(':another'), "monkey")

    def test_condition_single(self):
        """testing single condition nodes"""
        d1 = {
            "thing": {
                '/?foo': "kea",
                '/?bar': "pigeon",
                '/default': "sparrow"
            },
            "test1": "=:thing+foo",
            "test2": "=:thing+bar+foo",
            "test3": "=:thing+bar"
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(cnf.get(':thing'), "sparrow")
        self.assertEqual(cnf.get(':test1'), "kea")
        self.assertEqual(cnf.get(':test2'), "kea")
        self.assertEqual(cnf.get(':test3'), "pigeon")

    def test_condition_list(self):
        """testing list condition nodes"""
        d1 = {
            "thing": {
                '/#foo': "kea",
                '/#bar': "pigeon",
                '/default': "sparrow"
            },
            "thing2": {
                '/#foo': "kea",
                '/#bar': "pigeon"
            },
            "test1": "=:thing+foo",
            "test2": "=:thing+bar+foo",
            "test3": "=:thing+bar"
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(cnf.get(':thing'), ["sparrow"])
        self.assertEqual(cnf.get(':test1'), ["kea", "sparrow"])
        self.assertEqual(cnf.get(':test2'), ["kea", "pigeon", "sparrow"])
        self.assertEqual(cnf.get(':thing2'), [])

    def test_merge_cond(self):
        d1 = {
            'monkeys': [
                'mandrill',
                'baboon',
                'chimpanzee'
            ]
        }
        d2 = {
            'fail': {
                '/fail': True,
                '/true': False
            }
        }
        c1 = config.makeConfigVal(d1)
        c2 = config.makeConfigVal(d2)
        c1.merge(c2, config.ConfigEnv())
        d1.update(d2)
        self.assertEqual(c1.export(), d1)

class TestConfigLink(TestConfigNode):
    def setUp(self):
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.parent = config.ConfigDict({"target": 93}, self.ori, self.loc)
        self.value = "=..target"
        self.node = config.ConfigLink(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigLink

    def test_repr(self):
        self.assertEqual(self.node.__repr__(), f"Link(..target)")

    def test_delegate(self):
        nenv, nnode = self.node.delegate(self.env)
        self.assertEqual(nnode.getValue(nenv), 93)

    def test_getValue(self):
        self.assertEqual(self.node.getValue(self.env), 93)

    # merging doesn't do anything
    def test_merge_over(self):
        self.node.merge(config.ConfigLeaf(34), self.env, overwrite=True)
        self.assertEqual(self.node.getValue(self.env), 34)

    def test_merge_under(self):
        self.node.merge(config.ConfigLeaf(34), self.env, overwrite=False)
        self.assertEqual(self.node.getValue(self.env), 93)

    def test_dump(self):
        self.assertEqual(self.node.dump(), (self.value, []))

    def test_links(self):
        """testing = links"""
        d1 = {
            "mod1": {
                "monkey": "mandrill",
                "bird": {
                    "/color": "kea",
                    "/true": "magpipe"
                },
            },
            "mod2": {
                "animal": "=...mod1.monkey",
                "bird1": "=...mod1.bird",
                "bird2": "=...mod1.bird+color",
                "link": "=:mod1+color"
            }
        }
        node = config.makeConfigVal(d1)
        cnf = config.ConfigContext(node)

        self.assertEqual(cnf.get(':mod2.bird2'), 'kea')
        self.assertEqual(cnf.get(':mod2.animal'), 'mandrill')
        self.assertEqual(cnf.get(':mod2.bird1'), 'magpipe')

    def test_file_anchor(self):
        """Test the ; anchor"""
        node = config.makeConfigFromFile(pathlib.Path("tests/work/config/RR"))
        ctxt = config.ConfigContext(node)
        self.assertEqual(ctxt.get(".sub.thing"), "saw")

    def test_var_anchor(self):
        """Test the '$' anchor"""
        d1 = {
            'vars': {
                'link': '=:mod1.monkeys'
            },
            'mod1': {
                'monkeys': [
                    'mandrill',
                    'baboon',
                    'chimpanzee'
                ]
            },
            'mod2': {
                'sub': {
                    'sub2': {
                        'monkey': '=$link.1'
                    }
                }
            }
        }
        ctxt = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(ctxt.get(".mod2.sub.sub2.monkey"), "baboon")

    def test_weak_links(self):
        """test $ anchor with weak links"""
        d1 = {
            'vars': {
                'link1': '=:mod1',
                'link2': '=:mod2'
            },
            'mod1': "value1",
            'mod2': "value2",
            'mod3': "value3",
            'mod4': "value4",
            'node': {
                'vars': {
                    '?link2': '=:mod3',
                    '?link3': '=:mod4'
                },
                'test1': '=$link1', #not modifed -> value1
                'test2': '=$link2', #weak not overwrite -> value2
                'test3': '=$link3', #weak define -> value4
            }
        }
        ctxt = config.ConfigContext(config.makeConfigVal(d1))
        self.assertEqual(ctxt.get(".node.test1"), "value1")
        self.assertEqual(ctxt.get(".node.test2"), "value2")
        self.assertEqual(ctxt.get(".node.test3"), "value4")

    def test_options(self):
        """test links with option definition"""
        d1 = {
            'target': 'foo',
            'link': "=..target+num~5",
            'single': "=..target",
            'double': "=..single"
        }
        ctxt = config.ConfigContext(config.makeConfigVal(d1))
        mcfg = ctxt.move(".link").real()
        self.assertEqual(mcfg.pos(), config.ConfigPath(".target"))
        self.assertEqual(mcfg.flags()['num'], config.Option('num', 5))
        #
        self.assertEqual(ctxt.move(".single").pos(), config.ConfigPath(".single"))
        self.assertEqual(ctxt.move(".single").real().pos(), config.ConfigPath(".target"))
        self.assertEqual(ctxt.move(".double").real().pos(), config.ConfigPath(".target"))



class TestConfigImport(TestConfigNode):
    def setUp(self):   
        self.tmpDir = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self.tmpDir.name)
        (tmp / "target").mkdir() 
        with open(tmp / "target/RR", "w") as fh:
            print("487", file=fh)
        self.loc = config.Location(tmp)
        self.ori = config.Origin(13, 67)
        self.parent = config.ConfigNode()
        self.value = "+target"
        self.node = config.ConfigImport(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigImport

    def test_delegate(self):
        nenv, nnode = self.node.delegate(self.env)
        self.assertEqual(nnode.getValue(nenv), 487)
    
    def test_getValue(self):
        self.assertEqual(self.node.getValue(self.env), 487)

    def test_getLocation(self):
        self.assertEqual(self.node.getLocation(self.env), config.Location(self.loc / "target"))

    def test_dump(self):
        self.assertEqual(self.node.dump(), ("target/RR", []))
        
    # merging doesn't do anything
    def test_merge_over(self):
        self.node.merge(config.ConfigLeaf(34), self.env, overwrite=True)
        self.assertEqual(self.node.getValue(self.env), 34)

    def test_merge_under(self):
        self.node.merge(config.ConfigLeaf(34), self.env, overwrite=False)
        self.assertEqual(self.node.getValue(self.env), 487)

    def test_rr_import(self):
        """
        Tests if the import directive works
        """
        node = config.makeConfigFromFile(pathlib.Path("tests/work/config/RR"))
        ctxt = config.ConfigContext(node)
        self.assertEqual(ctxt.get(".monkey"), "mandrill")
        self.assertEqual(ctxt.get(".sub.bird"), "kea")
        self.assertEqual(ctxt.get(".sub2.weapon"), "stick")
        self.assertEqual(ctxt.get(".cnf.color"), "blue")
        
class TestConfigNode(unittest.TestCase):
    def setUp(self):
        self.parent = config.ConfigNode()
        self.loc = config.Location('loc')
        self.ori = config.Origin(13, 67)
        self.value = lua.LuaCtxt()
        self.node = config.ConfigRaw(self.value, self.ori, self.loc)
        self.node.setParent(self.parent, "key")
        self.env = config.ConfigEnv()
        self.cls = config.ConfigNode

class TestPath(unittest.TestCase):
    def test_create(self):
        paths = {
            ":foo": [
                (config.ConfigPathFunction.ROOT, None),
                (config.ConfigPathFunction.SELECT, "foo")
            ],
            ";foo$bar..blubber.#": [
                (config.ConfigPathFunction.FILE, None),
                (config.ConfigPathFunction.SELECT, "foo"),
                (config.ConfigPathFunction.VAR, "bar"),
                (config.ConfigPathFunction.UP, None),
                (config.ConfigPathFunction.SELECT, "blubber"),
                (config.ConfigPathFunction.SELECT, "#"),
            ],
            "" : [],
            "." : [],
            "..": [(config.ConfigPathFunction.UP, None)],
            ":" : [(config.ConfigPathFunction.ROOT, None)],
            "::": [(config.ConfigPathFunction.ROOT, None), (config.ConfigPathFunction.ROOT, None)],
            ":;": [(config.ConfigPathFunction.ROOT, None), (config.ConfigPathFunction.FILE, None)],
            ":$hallo": [(config.ConfigPathFunction.ROOT, None), (config.ConfigPathFunction.VAR, "hallo")],
        }
        noPaths = [
            'foo',
            ":foo.hel-lo.blubber"
        ]
        for spath,tups in paths.items():
            self.assertEqual(config.ConfigPath(spath).steps, tups)
        for spath in noPaths:
            with self.assertRaises(config.ConfigPathError) as ecm:
                config.ConfigPath(spath)


    def test_path_to_str(self):
        spaths = [':foo', ';foo$bar..blubber.#', '', ':', '..']
        trailDot = [':foo.', '.']
        for pth in spaths:
            p1 = config.ConfigPath(pth)
            self.assertEqual(pth, str(p1))
        for pth in trailDot:
            p1 = config.ConfigPath(pth)
            self.assertEqual(pth[:-1], str(p1))

    def test_slice(self):
        p1 = config.ConfigPath(":foo.bar.baz.blubber.blup.braaak")
        self.assertEqual(str(p1[:4]), ":foo.bar.baz")
        self.assertEqual(str(p1[4:]), ".blubber.blup.braaak")
        self.assertEqual(str(p1[4:6]), ".blubber.blup")
        self.assertEqual(str(p1[4]), ".blubber")

    def test_add(self):
        tests = [
            (".blubber.baz", "..", ".blubber.baz.."),
            (":foo.bar.baz", ".blubber.blup", ":foo.bar.baz.blubber.blup"),
            (":", ".blubber.blup", ":blubber.blup"),
            (":", ":", "::"),
            (".blubber", ":blub", ".blubber:blub"),
            (".blubber.", ".blub", ".blubber.blub"),
            ("", ":", ":"),
        ]
        for p1,p2,exp in tests:
            self.assertEqual(str(config.ConfigPath(p1) + config.ConfigPath(p2)), exp)

    def test_len(self):
        tests = [
            (":foo.bar.baz.blubber.blup.braaak", 7),
            (":", 1),
            ("", 0),
            (".", 0),
            (".blubber..blub", 3)
        ]
        for pth,exp in tests:
            self.assertEqual(len(config.ConfigPath(pth)), exp)

    def test_getElement(self):
        tests = [
            (":foo.bar.baz.blubber.blup.braaak", 2, (config.ConfigPathFunction.SELECT, "bar")),
            (":foo.bar.baz.blubber.blup.braaak", -2, (config.ConfigPathFunction.SELECT, "blup")),
            (":foo", 0, (config.ConfigPathFunction.ROOT, None))
        ]
        for pth, idx, exp in tests:
            self.assertEqual(config.ConfigPath(pth).getElement(idx), exp)

    def test_reduce(self):
        tests = [
            ("::", ":"),
            (":foo.bar.baz..blubber", ":foo.bar.blubber"),
            (".foo.bar:baz", ":baz"),
            (".foo.bar;;baz", ".foo.bar;baz"),
        ]
        for pth, exp in tests:
            self.assertEqual(str(config.ConfigPath(pth).reduced()), exp)

    def test_follow_root(self):
        node = config.ConfigNode()
        env = config.ConfigEnv()
        path = config.ConfigPath(":")
        nenv, nnode = path.follow(env, node)
        self.assertEqual(nenv.operation, ("Root",))
        
    def test_follow_child(self):
        node = config.makeConfigFromStr("""
          blubber:
            bla:
              baz: hallo
        """, config.Location(pathlib.Path('.')))
        env = config.ConfigEnv().derive(("Create",), move=config.ConfigPath(':'))
        path = config.ConfigPath(".blubber.bla")
        nenv, nnode = path.follow(env, node)
        self.assertEqual(nnode.getPath(), config.ConfigPath(".blubber.bla"))
        self.assertEqual(nenv.hist, config.ConfigPath(':blubber.bla'))

    def test_follow_up(self):
        node = config.makeConfigFromStr("""
          blubber:
            bla:
              baz: hallo
              baz2: welt
        """, config.Location(pathlib.Path('.')))
        env = config.ConfigEnv().derive(("Create",), move=config.ConfigPath(':'))
        path = config.ConfigPath(".blubber.bla.baz..baz2")
        nenv, nnode = path.follow(env, node)
        self.assertEqual(nnode.getPath(), config.ConfigPath(".blubber.bla.baz2"))
        self.assertEqual(nenv.hist, config.ConfigPath(':blubber.bla.baz..baz2'))

class TestOption(unittest.TestCase):
    def test_create(self): #just test that no exception are thrown
        config.Option("key", 12) #int
        config.Option("key2", 34.6) #float
        config.Option("key3", False) #bool
        config.Option("key4") #None
        config.Option("key5")
        with self.assertRaises(TypeError):
            config.Option("key6", "braak") #string

    def test_toString(self):
        self.assertEqual(str(config.Option("key", 12)), "key~12")
        self.assertEqual(str(config.Option("key", 3.4)), "key~3.4")
        self.assertEqual(str(config.Option("key", 0.00000034)), "key~3.4e-07")
        self.assertEqual(str(config.Option("key", 3.4e-7)), "key~3.4e-07")
        self.assertEqual(str(config.Option("key", True)), "key~true")
        self.assertEqual(str(config.Option("key")), "key")

    def test_fromString(self):
        self.assertEqual(config.Option.fromStr("key"), config.Option("key"))
        self.assertEqual(config.Option.fromStr("key~12"), config.Option("key", 12))
        self.assertEqual(config.Option.fromStr("key~3.4e-07"), config.Option("key", 3.4e-7))
        with self.assertRaises(config.OptionError):
            self.assertEqual(config.Option.fromStr("key~False"), config.Option("key", 12))
        self.assertEqual(config.Option.fromStr("key~true"), config.Option("key", True))

    def test_PathOption(self):
        pth, opts = config.parsePathOption(":foo.bar+key~12")
        self.assertEqual(pth, config.ConfigPath(":foo.bar"))
        self.assertListEqual(list(opts), [config.Option("key", 12)])
        

class TestConfigContext(unittest.TestCase):
    def test_traceback(self):
        d1 = {
            "mod1": {
                "animals": {
                    "monkey": "mandrill",
                    "bird": "kea"
                }
            },
            "mod2": {
                "link1": "=:mod1.animals",
                "link2": "=...mod1.animals"
            }
        }
        cnf = config.ConfigContext(config.makeConfigVal(d1))
        c1 = cnf.move(".mod2.link1.bird")
        backtrace = c1.path()
        self.assertEqual(backtrace, config.ConfigPath(".mod2.link1:mod1.animals.bird"))
        c2 = cnf.move(".mod2.link2.monkey")
        backtrace = c2.path()
        self.assertEqual(backtrace, config.ConfigPath(".mod2.link2...mod1.animals.monkey"))


    def test_crumbs(self):
        d1 = {
            "mod1": {
                "monkey": "mandrill",
                "bird": "kea"
            },
            "mod2": {
                "animal": "=...mod1.monkey",
                "bird1": "=...mod1.bird",
            }
        }
        node = config.makeConfigVal(d1)
        env = config.ConfigEnv()
        path = config.ConfigPath(":mod2.animal")
        nenv, nnode = path.follow(env, node)
        lines = nenv.dump()
        exp = [
            'ConfigEnv(:mod2.animal,) - trace:',
            '  @:mod2.animal                             - DictChild animal',
            '  @:mod2                                    - DictChild mod2',
            '  @:                                        - Root',
            '  @                                         - Follow _ :mod2.animal',
            '  @                                         - Env'
        ]
        self.assertListEqual(lines, exp)

    def test_errors(self):
        d1 = {
            "mod1": {
                "monkey": "mandrill",
                "bird": "kea"
            },
            "mod2": {
                "animal": "=...mod1.monkey",
                "bird1": "=...mod1.bird",
                "bird2": "=...mod1.bird2"
            }
        }
        expDump = [
            "PathNotExist: child:bird2 does not exist",
            '  ConfigDict(size:2)\n    @.mod1',
            "  ConfigEnv(:mod2.bird2...mod1,) - trace:",
            '    @:mod2.bird2...mod1                       - DictChild mod1',
            '    @:mod2.bird2...                           - Up',
            '    @:mod2.bird2..                            - Up',
            '    @:mod2.bird2                              - Follow LinkFollow ...mod1.bird2',
            '    @:mod2.bird2                              - DictChild bird2',
            '    @:mod2                                    - DictChild mod2',
            '    @:                                        - Root',
            '    @                                         - Follow CtxtGet :mod2.bird2',
            '    @                                         - ContextCreate',
            '    @                                         - Env'
        ]
        ctxt = config.ConfigContext(config.makeConfigVal(d1))

        with self.assertRaises(config.PathNotExist) as ecm:
            ctxt.get(":mod2.bird2")
        
        lst = ecm.exception.dump()

        self.assertListEqual(ecm.exception.dump(), expDump)

        
        with self.assertRaises(config.PathNotExist) as ecm:
            ctxt.get(":mod2.bird3")

    def test_setpath(self):
        """testing the creation of nodes with set()"""
        exp = {
            "node": {
                "key1": "funky",
                "key2": "groovy"
            },
            "value": "foo",
            "list": ["hammer", "drill"]
        }
        ctxt = config.ConfigContext(config.makeConfigVal({}))
        ctxt.set(".node.key1", "funky", create=True)
        ctxt.set(".node.key1", "funky")
        ctxt.set(".node.key2", "groovy")
        ctxt.set(".value", "foo", create=True)
        ctxt.set(".list.#", "hammer", create=True)
        ctxt.set(".list.#", "drill", create=False)
        with self.assertRaises(config.PathNotExist) as ecm:
            ctxt.set(".node2.value", "foo")
        self.assertEqual(ctxt.get(''), exp)


    def test_setmerge_root(self):
        o1 = {
            'var1': 'val1',
            'var2': 'val2',
            'node1': {
                'node1-var1': 'val1',
                'node1-var2': 'val2'
            }
        }
        o2 = {
            'var2': 'val2_over',
            'var3': 'val3',
            'node1': {
                'node1-var3': 'val3'
            }
        }
        exp = {
            'var1': 'val1',
            'var2': 'val2_over',
            'var3': 'val3',
            'node1': {
                'node1-var1': 'val1',
                'node1-var2': 'val2',
                'node1-var3': 'val3'
            }
        }
        ctxt = config.ConfigContext(config.makeConfigVal(o1))
        ctxt.set("", o2, merge=True)
        self.assertEqual(ctxt.get(''), exp)

    def test_setmerge(self):
        o1 = {
            'var1': 'val1',
            'var2': 'val2',
            'node1': {
                'node1-var1': 'val1',
                'node1-var2': 'val2'
            }
        }
        o2 = {
            'node1-var3': 'val3',
            'node1-var2': 'val2_over'
        }
        exp = {
            'var1': 'val1',
            'var2': 'val2',
            'node1': {
                'node1-var1': 'val1',
                'node1-var2': 'val2_over',
                'node1-var3': 'val3'
            }
        }
        ctxt = config.ConfigContext(config.makeConfigVal(o1))
        ctxt.set(".node1", o2, merge=True)
        self.assertEqual(ctxt.get(''), exp)


    def test_assimilate(self):
        base = """
          node:
            foo:
              monkey: mandrill
              bird: kea
        """
        add = """
          foo:
            mammal: cat
          bar: dog
        """
        exp = {
            "node": {
                "foo": {
                    "monkey": "mandrill",
                    "bird": "kea",
                    "mammal": "cat"
                },
                "bar": "dog"
            }
        }
        cfg = config.ConfigContext(config.makeConfigFromStr(base, config.Location("base")))
        node = config.makeConfigFromStr(add, config.Location("add"))
        cfg.assimilate(".node", node, merge=True)
        self.assertEqual(cfg.get(''), exp)

    def test_dump(self):
        """Test the dump formating"""
        d1 = {
            "mod1": {
                "monkey": "mandrill",
                "bird": {
                    "/color": "kea",
                    "/true": "magpipe"
                },
            },
            "mod2": {
                "animal": "=...mod1.monkey",
                "bird1": "=...mod1.bird",
                "bird2": "=...mod1.bird+color",
                "link": "=:mod1+color"
            }
        }
        exp = [
            " # ",
            "mod1: ",
            "  monkey: mandrill",
            "  bird: ",
            "    /color: kea",
            "    /true: magpipe",
            "mod2: ",
            "  animal: =...mod1.monkey",
            "  bird1: =...mod1.bird",
            "  bird2: =...mod1.bird+color",
            "  link: =:mod1+color"
        ]
        ctxt = config.ConfigContext(config.makeConfigVal(d1))
        msg = ctxt.dump()
        for line,eLine in zip(msg, exp):
            self.assertEqual(line, eLine)
        self.assertEqual(len(msg), len(exp))

    def test_iter(self):
        """Testing iteration of ConfigDicts and ConfigLists"""
        d1 = {
            'monkeys': [
                'mandrill',
                'baboon',
                'chimpanzee'
            ],
            'animals': {
                'monkey': 'mandrill',
                'bird': 'kea',
                'fish': 'shark'
            }
        }
        ctxt = config.ConfigContext(config.makeConfigVal(d1))
        expList = [
            ('0', 'mandrill'),
            ('1', 'baboon'),
            ('2', 'chimpanzee')
        ]
        expDict = {
            'monkey': 'mandrill',
            'bird': 'kea',
            'fish': 'shark'
        }

        for tup,etup in zip(ctxt.move('.monkeys'), expList):
            key, cctxt = tup
            val = cctxt.get('')
            self.assertEqual((key, val), etup)

        for tup,etup in zip(ctxt.move('.animals'), expDict.items()):
            key, cctxt = tup
            val = cctxt.get('')
            self.assertEqual((key, val), etup)

    def test_leafs(self):
        """Testing iteration leaf values"""
        d1 = {
            'monkeys': [
                'mandrill',
                'baboon',
                'chimpanzee'
            ],
            'animals': {
                'monkey': 'mandrill',
                'bird': 'kea',
                'fish': 'shark'
            }
        }
        ctxt = config.ConfigContext(config.makeConfigVal(d1))
        exp = [
            ('.monkeys.0', 'mandrill'),
            ('.monkeys.1', 'baboon'),
            ('.monkeys.2', 'chimpanzee'),
            ('.animals.monkey', 'mandrill'),
            ('.animals.bird', 'kea'),
            ('.animals.fish', 'shark')
        ]
        leafs = list(ctxt.leafs())
        self.assertListEqual(leafs, exp)

    def test_export(self):
        d1 = {
            'monkeys': [
                'mandrill',
                'baboon',
                'chimpanzee'
            ],
            'animals': {
                'monkey': 'mandrill',
                'bird': 'kea',
                'fish': 'shark'
            },
            "link": "=..monkeys.1",
            "script": "$a +4",
            "program": """$$
                return 'hallo'""",
            "cond": {
                "/FLAG": "grün",
                "/OTHER": "blau",
                "/true": "weiß"
            },
            "import": "+_",
            "import2": "+sub",
            "import3": "#sub2/thing.yaml"
        }
        node = config.makeConfigVal(d1)
        expo = node.export()
        self.assertEqual(d1, expo)

    def test_travers(self):
        d1 = {
            "sv": "module.sv",
            "inc": [
                {"sv": "sub1.sv"},
                {"sv": "sub2.sv"}
            ]
        }
        node = config.makeConfigVal(d1)
        cfg = config.ConfigContext(node)
        lst = []
        for vcfg in cfg.travers():
            lst.append(vcfg.get(".sv"))
        self.assertListEqual(lst, ["sub1.sv", "sub2.sv", "module.sv"])

class TestConfig(unittest.TestCase):
    def test_conf_to_from_str(self):
        src = """monkey: mandrill
sub: +_
sub2: +_
cnf: +#cnf.yaml
somefile: somefile.txt
number: 4711
jubjub_error:
  tool: BuiltIn.jabberwocky
  fail:
    /fail: true
    /true: false
  noret:
    /noret: true
    /true: false
jubjub_fail: =..jubjub+fail
jubjub_noret: =..jubjub+noret
"""
        node = config.makeConfigFromStr(src, None)
        dst = config.writeConfigToStr(node)
        print(dst)
        for line in src.splitlines():
            self.assertIn(line, dst.splitlines())


if __name__ == '__main__':
    unittest.main()

## produces a netlist
## synth:
##   tool:
##     /VIVADO: Vivado.synth
##     /default: yosys

## uses a netlist
## 2nd:
##   tool:
##     /VIVADO: Vivado.sim
##     /default: icarus
##   inc:
##     - =;netlist

## netlist:
##   sv:
##     /VIVADO: =;viv.synth~sv
##     /default: =;synth~sv

## viv:
##   synth: =;synth+VIVADO
##   2nd: =;2nd+VIVADO


## results:
## synth  
## viv.synth


## calling
## :viv.2nd


