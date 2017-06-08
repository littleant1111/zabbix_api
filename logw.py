# -*- coding:utf-8 -*-
#!/bin/env python

import logging

def log_w(_debuglevel, _filename):
    logging.basicConfig(level=_debuglevel,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=_filename,
                        filemode='a')
