# -*- coding: utf-8 -*-
from docutils import nodes

from docutils.parsers.rst import Directive

from sphinx.locale import _

import requests
import json

class swaggerdoc(nodes.Admonition, nodes.Element):
    pass

def visit_swaggerdoc_node(self, node):
    self.visit_admonition(node)

def depart_swaggerdoc_node(self, node):
    self.depart_admonition(node)

class SwaggerDocDirective(Directive):

    # this enables content in the directive
    has_content = True

    def processSwaggerURL(self, url):
        r = requests.get(url)

        return r.json()['apis']

    def create_item(self, key, value):
        para = nodes.paragraph()
        para += nodes.strong('', key)
        para += nodes.Text(value)

        item = nodes.list_item()
        item += para

        return item

    def expand_values(self, list):
        expanded_values = ''
        for value in list:
            expanded_values += value + ' '

        return expanded_values

    def create_parameter(self, param):

        content = nodes.paragraph()
        content += nodes.strong('', nodes.Text(param['name'], param['name']))
        if 'description' in param:
            content += nodes.Text(" - " + param['description'])

        bullet_list = nodes.bullet_list()

        if 'type' in param:
            bullet_list += self.create_item('Type: ', param['type'])

        if 'paramType' in param:
            bullet_list += self.create_item('Param Type: ', param['paramType'])

        if 'defaultValue' in param:
            bullet_list += self.create_item('Default Value: ', param['defaultValue'])

        if 'minimum' in param:
            bullet_list += self.create_item('Minimum: ', param['minimum'])

        if 'maximum' in param:
            bullet_list += self.create_item('Maximum: ', param['maximum'])

        if 'enum' in param:
            bullet_list += self.create_item('Alternatives: ', ", ".join(param['enum']))

        if 'format' in param:
            bullet_list += self.create_item('Format: ', param['format'])

        content += bullet_list

        return content

    def make_operation(self, path, operation):
        swagger_node = swaggerdoc(path)
        swagger_node += nodes.title(path, operation['method'].upper() + ' ' + path)

        content = nodes.paragraph()
        content += nodes.Text(operation['summary'])

        bullet_list = nodes.bullet_list()
        if 'consumes' in operation:
            bullet_list += self.create_item('Consumes: ', self.expand_values(operation.get('consumes', '')))
        if 'produces' in operation:
            bullet_list += self.create_item('Produces: ', self.expand_values(operation.get('produces', '')))

        content += bullet_list

        if 'parameters' in operation:
            p = nodes.paragraph()
            p += nodes.strong('', "Parameters")
            content += p
            param_list = []
            for param in operation.get('parameters', []):
                param_list += self.create_parameter(param)
            content += param_list
        swagger_node += content

        return [swagger_node]

    def run(self):
            methods = self.processSwaggerURL(self.content[0])

            entries = []

            for method in methods:
                for operation in method['operations']:
                    entries += self.make_operation(method['path'], operation)

            return entries
