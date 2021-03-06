#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml

def get_cluster_config_file():
    '''Returns the file used as DCOS architecture'''
    return "config.yml"

def get_cluster_config_yml():
    '''Returns a list with hostname and IP'''
    with open(get_cluster_config_file(), 'r') as f:
        ret = yaml.load(f)

    return ret

cluster_yml = get_cluster_config_yml()

class InventoryTemplate:
    _template = """
{
    "all": {
        "hosts": [%(_get_all|_pattern_a)s],
        "vars": {
            "ansible_user": "vagrant",
            "ansible_become": "true"
        }
    },
    "bootstrap": {
        "hosts": ["boot"]
    },
    "masters": {
        "hosts": [%(_get_masters|_pattern_a)s],
        "vars": {
            "node_type": "master"
        }
    },
    "agents": {
        "children": ["agents-private", "agents-public"]
    },
    "agents-private": {
        "hosts": [%(_get_privates|_pattern_a)s],
        "vars": {
            "node_type": "slave"
        }
    },
    "agents-public": {
        "hosts": [%(_get_publics|_pattern_a)s],
        "vars": {
            "node_type": "slave_public"
        }
    },
    "_meta": {
        "hostvars": {
            %(_get_all_hostip|_pattern_b)s
        }
    }
}
    """

    def __init__(self, dict={}):
        self.dict = dict

    def __str__(self):
        return self._template % self

    def __getitem__(self, key):
        return self._process(key.split("|"))

    def _process(self, l):
        arg = l[0]
        if len(l) == 1:
            if arg in self.dict:
                return self.dict[arg]
            elif hasattr(self, arg) and callable(getattr(self, arg)):
                return getattr(self, arg)()
            else:
                raise KeyError(arg)
        else:
            func = l[1]
            return getattr(self, func)(self._process([arg]))

    def _get_all(self):
        cad = []
        for i in cluster_yml:
            cad.append(i)
        return cad

    def _get_masters(self):
        cad = []
        for i in cluster_yml:
            if cluster_yml[i].get('type') == 'master':
                cad.append(i)
        return cad

    def _get_privates(iself):
        cad = []
        for i in cluster_yml:
            if cluster_yml[i].get('type') == 'agent-private':
                cad.append(i)
        return cad

    def _get_publics(iself):
        cad = []
        for i in cluster_yml:
            if cluster_yml[i].get('type') == 'agent-public':
                cad.append(i)
        return cad

    def _get_all_hostip(self):
        cad = []
        for i in cluster_yml:
            cad.append("\"%s\": {\"ansible_host\": \"%s\"}" % (i, cluster_yml[i].get('ip')))
        return cad

    def _pattern_a(self, l):
        return ",".join(["\"%s\"" % x for x in l])

    def _pattern_b(self, l):
        return ",".join(["%s" % x for x in l])

print(InventoryTemplate())