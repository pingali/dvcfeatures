#!/usr/bin/env python3

"""
Intended to manage 
"""

import os
import sys
import json
import subprocess 
import click

bindir = os.path.abspath(os.path.dirname(__file__))
rootdir = os.path.abspath(os.path.join(bindir, '..'))
etcdir = os.path.join(rootdir, 'etc')
datadir = os.path.join(rootdir, 'data')

# Get dictionary merge 
sys.path.append(bindir)
from lib import merge

def get_config():

    conf = os.path.join(etcdir, 'datasets.json')
    conf = json.load(open(conf))

    localconf = os.path.join(etcdir, 'datasets.local.json')
    if os.path.exists(localconf):
        localconf = json.load(open(localconf))
        merge(conf, localconf)

    # => Resolve paths 
    params = conf.get('params',{})
    for d in conf['datasets']:
        context = params.copy()
        context.update({
            'dataset': d
        })

        for var in ['root', 'remote']: 
            if var  in conf['datasets'][d]:
                #=> Update the datasets
                value = conf['datasets'][d][var]
                value = os.path.expandvars(value)
                value = value % context
                conf['datasets'][d][var] = value
            
    return conf
        
    
@click.group()
def process():
    """
    Manage feature datasets in DVC
    """
    pass

@process.command("show")
def _show():
    """
    Show configured datasets 
    """
    conf = get_config() 
    print(json.dumps(conf, indent=4))    

@process.command("add-dataset")
@click.argument("link") 
@click.argument("root") 
def _add_dataset(link, root):
    """
    Add dataset
    """

    pass

if __name__ == "__main__":
    process() 
    
