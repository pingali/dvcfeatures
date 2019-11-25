#!/usr/bin/env python3

"""
Intended to manage
"""

import os
import sys
import json
import click
import traceback

bindir = os.path.abspath(os.path.dirname(__file__))
rootdir = os.path.abspath(os.path.join(bindir, '..'))
etcdir = os.path.join(rootdir, 'etc')
datadir = os.path.join(rootdir, 'datasets')

# Get dictionary merge
sys.path.append(bindir)
from lib import merge, cwd, run


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

@process.command("list")
def _list():
    """
    List configured datasets
    """
    conf = get_config()
    datasets = conf['datasets']
    for name, detail in datasets.items():
        print(name)
        print("   Root:", detail['root'])

@process.command("show")
@click.option("--dataset",
              default=None,
              help="Name of the dataset")
def _show(dataset):
    """
    List configured datasets
    """
    conf = get_config()
    datasets = conf['datasets']
    for name, detail in datasets.items():
        if ((dataset is not None) and (dataset != name)):
            continue

        print(name,":")
        print("   Root:", detail['root'])
        print("   Units:")
        for d in os.listdir(os.path.join(datadir, name, 'data')):
            if d == '.ignore':
                continue
            print("        ", d)

@process.command("init")
@click.option("--dataset",
              default=None,
              help="Name of the dataset")
def _init(dataset):
    """
    Initialize the directories but dont commit
    """
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
        if os.path.exists(datalink):
            os.remove(datalink)
        os.symlink(root, datalink)
        print(u'\u2713' + " " + name)

@process.command("update")
@click.argument("dataset")
@click.argument("unit")
@click.option("--message", '-m',
              default=None,
              help="Git message")
def _update(dataset, unit, message):
    """
    Update repo with given unit of dataset
    """

    conf = get_config()
    if dataset not in conf['datasets']:
        print("Unknown datasets. Please use 'show' to see the available datasets")
        return

    workingdir = os.path.join(datadir, dataset)
    detail = conf['datasets'][dataset]
    try:

        with cwd(workingdir):
            # Add the unit to the
            print(os.getcwd())

            cmd = ['dvc', "add", "data/{}".format(unit)]
            run(cmd)

        cmd = ['git', "add", "datasets"]
        run(cmd)

        if message is None:
            message = "Automated commit of the dataset update"
        cmd = ['git', "commit", '-a', '-m', message]
        run(cmd)

        cmd = ['git', "push", "origin"]
        run(cmd)

        #cmd = ["dvc", "push"]
        #run(cmd)

    except:
        traceback.print_exc()


if __name__ == "__main__":
    process()

