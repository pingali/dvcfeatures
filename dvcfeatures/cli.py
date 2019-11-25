#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import click
import traceback

bindir = os.path.abspath(os.path.dirname(__file__))
rootdir = os.getcwd()
datadir = os.path.join(rootdir, 'datasets')

############################################
# Helper libraries...
############################################
from .lib import merge, cwd, run

def get_config(filename='datasets.json'):

    conf = os.path.join(rootdir, 'datasets.json')
    conf = json.load(open(conf))

    localconf = os.path.join(rootdir, 'local.' + filename)
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

############################################
# Command line
############################################

@click.group()
def process():
    """
    Manage feature datasets in DVC
    """
    pass

@process.command("init")
@click.option("--dataset",
              default=None,
              help="Name of the dataset")
def _init(dataset):
    """
    Initialize the directories but dont commit
    """

    # => Check if right ignore commands are present
    if os.path.exists(".gitignore"):
        content = open(".gitignore").read()
    else:
        content = ""
        
    if "local.datasets.json" not in content:
        content += "\n#DVC Features\nlocal.datasets.json\ndata\n"
        with open('.gitignore', 'w') as fd:
            fd.write(content)
            print(u'\u2713' + " [.gitignore] " + "Added local.datasets.json & data")
    else:
        print(u'\u2713' + " [.gitignore] " + "Checked")

    # Now go through each of the datasets and create appropriate
    # directories
    conf = get_config()
    for name, detail in conf['datasets'].items():

        if ((dataset is not None) and (dataset != name)):
            continue

        path = os.path.join(datadir, name)
        try:
            os.makedirs(path)
        except:
            pass

        # Create a link to the data directory
        root = detail['root']
        datalink = os.path.join(datadir, name, 'data')
        if os.path.islink(datalink):
            os.remove(datalink)
        os.symlink(root, datalink)
        print(u'\u2713' + " [dataset] " + name)


@process.command("list")
@click.option("--config", '-c',
              default='datasets.json',
              help="Configuration file")
def _list(config):
    """
    List configured datasets
    """
    conf = get_config(config)
    datasets = conf['datasets']
    for name, detail in datasets.items():
        print(name)
        print("   Root:", detail['root'])

@process.command("show")
@click.argument('dataset')
@click.option("--config", '-c',
              default='datasets.json',
              help="Configuration file")
def _show(dataset,config):
    """
    Show dataset details

    use 'all' for dataset to show all
    """
    conf = get_config(config)
    datasets = conf['datasets']
    for name, detail in datasets.items():
        if ((dataset != 'all') and (dataset != name)):
            continue

        print(name,":")
        print("   Root:", detail['root'])
        print("   Units:")
        for d in os.listdir(os.path.join(datadir, name, 'data')):
            if d == '.gitignore':
                continue
            dvcfile = os.path.join(datadir, name, d + ".dvc")

            inrepo = ""
            if os.path.exists(dvcfile):
                inrepo = u'\u2713' + " Versioned" 
            print("        ", d, inrepo)

@process.command("update")
@click.argument("dataset")
@click.argument("unit")
@click.option("--message", '-m',
              default=None,
              help="Git message")
@click.option("--config", '-c',
              default='datasets.json',
              help="Configuration file")
def _update(dataset, unit, message,config):
    """
    Update repo with given unit of dataset
    """

    conf = get_config(config)
    if dataset not in conf['datasets']:
        print("Unknown datasets. Please use 'show' to see the available datasets")
        return

    workingdir = os.path.join(datadir, dataset)
    detail = conf['datasets'][dataset]
    try:

        # Get the remote 
        remote = detail.get('remote', conf.get('remote', None))
        
        with cwd(workingdir):
            # Add the unit to the
            print("Working dir", os.getcwd())

            cmd = ['dvc', "add", "data/{}".format(unit)]
            run(cmd)

        cmd = ['git', "add", "datasets"]
        run(cmd)

        if message is None:
            message = "Automated commit of the dataset update"
        cmd = ['git', "commit", '-a', '-m', message]
        run(cmd)

        cmd = ["dvc", "push"]
        if remote is not None:
            cmd.extend(['-r', remote])
        run(cmd)

        cmd = ['git', "push", "origin"]
        run(cmd)

        # Free up space
        cmd = ['dvc',  'gc', '-f']
        run(cmd)


    except:
        traceback.print_exc()

def main():
    process()
    
if __name__ == "__main__":
    process()

