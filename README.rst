How to use regression tests
---------------------------
**If regression tests are already installed, skip to step 5.

1)Create your test files.
2)Download the plugin package.
3)Change directories into the plugin folder
4)Run `pip install -e .'
5)Run `nosetests --with-regression' where you would normally run
    your nose tests
6)???
7)Profit while you look at your fancy new reg_settings.py


Output
------
At the end of the nosetest output, Nose Regression will print out 
any tests that used to fail but now pass (if any) and any tests that 
should pass but happened to fail (if any).  All tests are separated 
and say which module they're from.


Options
-------
-n/--new    Run tests that should fail to quickly see if any tests 
                are now functional
-r/--reg    Run tests that shouldn't fail to quickly see if any tests 
                are now broken
-W          Don't write to reg_settings.py
-f/--file   Specify which reg_settings.py file you want to use 
                (not completely functional)

Inside the reg_settings.py file, there's an options dictionary at the top.  
If you want any options to always run (excluding -f/--file) place the short 
option as the key and any required values as the value. Currently just leave 
the value as '' as the only option requiring a value is -f/--file.


Notes
-----
This plugin does not yet fully support methods, only functions. Please note 
this when creating tests you want to use with this plugin.

Thanks for using it! :)
