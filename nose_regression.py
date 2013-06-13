from nose.plugins import Plugin
from nose.failure import Failure

import os, sys
sys.path.append(os.getcwd())

try:
    import reg_settings as settings
except ImportError:
    with open('reg_settings.py', 'w') as f:
        f.write('options={}\n')
        f.write('tests=[]\n')
        f.write('should_fail=[]\n')
    import reg_settings as settings

class Regression(Plugin):
    """
    Does simple regression testing to make running larger projects easier when 
    there's a lot to test.
    """
    name = "regression"
    enabled = True

    failed_reg = 0
    broken_tests = []
    new_passed = 0
    fixed_tests = []

    #flags
    _write = False
    _reg = False
    _new = False
    _settings = ''

    #list of things to add/remove
    new_tests = []
    new_failed = []

    def addSuccess(self, test):
        """
        Called when a test passes.  If it used to fail, add it to the list of 
        fixed tests.
        """
        setattr(test.test.test, 'failed', False)
        if test.test.test.__name__ in settings.should_fail:
            self.new_passed += 1
            self.fixed_tests.append(test.test.test)

    def addError(self, test, err):
        """
        Called when a test raises an uncaught exception.  If it shouldn't fail 
        add it to the list of broken tests.
        """
        if not hasattr(test, 'test') or isinstance(test.test, Failure):
            return
        setattr(test.test.test, 'failed', True)
        if not test.test.test.__name__ in settings.should_fail and \
                test.test.test.__name__ in settings.tests:
            self.failed_reg += 1
            self.broken_tests.append(test.test.test)

    def addFailure(self, test, err):
        """
        Called when a test fails.  If it shouldn't fail, add it to the list of 
        broken tests.
        """
        setattr(test.test.test, 'failed', True)
        if not test.test.test.__name__ in settings.should_fail and \
                test.test.test.__name__ in settings.tests:
            self.failed_reg += 1
            self.broken_tests.append(test.test.test)

    def afterTest(self, test):
        """
        When a test is finished, save whether or not it should fail in future
        tests to reg_settings.py.
        """
        if not hasattr(test, 'test') or isinstance(test.test, Failure):
            return

        if not test.test.test.__name__ in settings.tests:
            self.new_tests.append(test.test.test.__name__)
            if getattr(test.test.test, 'failed', False):
                self.new_failed.append(test.test.test.__name__)
        
    def report(self, stream):
        """
        Called after all error output is printed.  Prints out which tests have 
        been fixed and which tests are now broken.
        """
        stream.writeln('-'*69)
        stream.writeln('Regression testing results:\n')
        if not self.new_passed:
            stream.writeln('No new tests have passed.')
        else:
            stream.write('%d new test(s) now successfully run: \n\t' % (self.new_passed))
            stream.write(',\n\t'.join([f.__module__ + '.' + f.__name__ for f in self.fixed_tests]))
            stream.writeln()
        stream.writeln()
        if not self.failed_reg:
            stream.writeln('No tests failed their regression test.')
        else:
            stream.write('%d test(s) failed their regression test: \n\t' % (self.failed_reg))
            stream.write(',\n\t'.join([f.__module__ + '.' + f.__name__ for f in self.broken_tests]))
            stream.writeln()

        #Handle rewriting to the settings file
        if self._write:
            self.write_to_file()

    def options(self, parser, env):
        """
        Called to allow the plugin to register command line options with the 
        parser.
        -W          - don't write values to reg_settings
        -r/--reg    - only run regression tests
        -n/--new    - only run tests that should fail
        -f/--file   - path to reg_settings.py
        """
        booloptions = [
            (('-W',), 'store_true', 'nwrite', 
                    "Don't write values into reg_settings",),
            (('-r','--reg'), 'store_true', 'regonly', 
                    "Only run regression tests",),
            (('-n','--new'), 'store_true', 'newonly', 
                    "Only run tests that should fail",),
            ]
        options = [
            (('-f','--file'), 'store', 'filename', 
                    "Path to reg_settings.py", 'FILE',),
            ]
        for com, action, dest, help in booloptions:
            if com[0] in settings.options:
                parser.add_option(*com, action=action, dest=dest, 
                                    help=help, default=True)
            else:
                parser.add_option(*com, action=action, dest=dest, 
                                    help=help, default=False)
        for com, action, dest, help, metavar in options:
            if com[0] in settings.options:
                parser.add_option(*com, action=action, dest=dest, 
                                    help=help, metavar=metavar, 
                                    default=settings.options[com[0]])
            else:
                parser.add_option(*com, action=action, dest=dest, help=help, 
                                metavar=metavar, default=settings.__file__)
        Plugin.options(self, parser, env=env)

    def configure(self, options, conf):
        """
        Called after the command line parser has been parsed.
        Errors if -r and -n are both set.
        """
        Plugin.configure(self, options, conf)
        if not self.enabled:
            return
        self._write = not options.nwrite
        self._reg = options.regonly
        self._new = options.newonly
        self._settings = options.filename
        if self._reg and self._new:
            options.error("-r and -n are mutually exclusive")

    def wantFunction(self, function):
        """
        Decides whether the plugin wants to use the function.

        If -r is set, then it will only return tests that shouldn't fail.
        If -n is set, then it will only return tests that should fail.
        Otherwise it doesn't care.
        """
        if self._reg: #run tests that shouldn't fail
            if function.__name__ in settings.should_fail:
                return False
            return None
        if self._new: #run tests that should fail
            if function.__name__ in settings.should_fail:
                return None
            return False
        return None

    def write_to_file(self):
        """
        Gets the plugin ready to write all the data to the reg_settings.py file.
        Adds in any new tests, adds in any new tests that should fail, and takes 
        out any fixed tests.
        """
        changed = False
        if self.new_tests:
            settings.tests.extend(self.new_tests)
            changed = True
        if self.new_failed:
            settings.should_fail.extend(self.new_failed)
            changed = True
        if self.fixed_tests:
            for test in self.fixed_tests:
                settings.should_fail.remove(test.__name__)
            changed = True
        if changed:
            write(self._settings, settings.options, 
                    settings.tests, settings.should_fail)

def write(filename, options={}, tests=[], should_fail=[]):
    """
    Writes the inputs into a file.
    @params
    options     - a dictionary of options to always be set
    tests       - a list of all the tests run
    should_fail - a list of tests that should fail
    """
    with open(filename, 'w') as f:
        f.write("options={\n\t" + 
            ",\n\t".join(
                [("'"+k+"':'"+v+"'") for k,v in settings.options.items()]) + 
            "}\n")
        f.write("tests=[\n\t" + 
            ",\n\t".join(["'" + test + "'" for test in settings.tests]) + 
            "]\n")
        f.write("should_fail=[\n\t" + 
            ",\n\t".join(["'" + test + "'" for test in settings.should_fail]) + 
            "]\n")
