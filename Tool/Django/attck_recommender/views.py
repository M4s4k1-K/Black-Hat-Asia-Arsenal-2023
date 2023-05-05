from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .forms import UploadCSVForm
from attck_recommender.models import *
from neo4j import GraphDatabase
from neo4j.debug import watch
import configparser
import json
import os
import uuid
import re
import ast

#neo4j code
driver = settings.DRIVER

def make_adversary_used_edge(tx, techniques):
    for technique in techniques:
        tx.run('MATCH (g:Group {name: "Adversary"}) '
               'MATCH (t:Technique {name: $technique}) '
               'CREATE (g)-[:USED]->(t)',
               technique=technique)

def update_input_property(tx):
    tx.run('MATCH (a:Group {name: "Adversary"})-[:USED]->(t:Technique) '
            'WITH a,t '
            'SET t.input=1')

def update_similarity_property(tx):
    tx.run('MATCH (a:Group {name: "Adversary"})-[:USED]->(ct:Technique)<-[:USED]-(g:Group) '
            'WITH a, g, COUNT(ct) AS intersection '
            'MATCH (g)-[:USED]->(gt:Technique) '
            'WITH a, g, intersection, COUNT(gt) AS g_size '
            'MATCH (a)-[:USED]->(at:Technique) '
            'WITH a, g, intersection, g_size, ((2.0*intersection)/(COUNT(at) + g_size)) AS dice '
            'SET g.similarity=dice')

def update_weight_property(tx):
    tx.run('MATCH (g:Group) WHERE ((g.name <> "Adversary") AND (g.similarity>0.0)) '
            'WITH g ORDER BY g.similarity DESC LIMIT 60 '
            'WITH collect(g.name) AS top_kg_list '
            'UNWIND top_kg_list AS tkg '
            'MATCH (kg{name:tkg})-[u:USED]->(t:Technique) '
            'WITH kg,u '
            'SET u.weight=((1.0)/(1.0-kg.similarity))')

def update_sr_property(tx):
    tx.run('MATCH (g:Group)-[u:USED]->(t:Technique) WHERE (g.name <> "Adversary") '
            'WITH t, (sum(u.weight)/60.0) AS sr '
            'SET t.sr=sr')

def update_recommend_property(tx):
    tx.run('MATCH (a:Group {name: "Adversary"})-[:USED]->(t:Technique) '
            'WITH max(t.e_stage) AS mls '
            'MATCH (t:Technique) WHERE ((t.input=0) AND (t.sr>=0.17) AND (t.l_stage>=mls)) '
            'WITH t '
            'SET t.recommend=1')

def delete_adversary_used_edge(tx):
    tx.run('MATCH (:Group{name:"Adversary"})-[u:USED]->(:Technique) DELETE u')

def reset_group_property(tx):
    tx.run('MATCH (g:Group) WHERE (g.name <> "Adversary") '
            'SET g.similarity=0.0')

def reset_technique_property(tx):
    tx.run('MATCH (t:Technique) '
            'SET t.recommend=0, t.input=0, t.sr=0.0')

def reset_used_property(tx):
    tx.run('MATCH ()-[u:USED]->() SET u.weight=0.0')


def get_recommended_techniques(tx):
    result=tx.run('MATCH (t:Technique) WHERE t.recommend=1 RETURN t.name, t.value')
    return [{"name": r["t.name"], "value": r["t.value"]} for r in result]


def make_adversary(techniques):
    with driver.session() as session:
        session.write_transaction(make_adversary_used_edge, techniques)
        session.write_transaction(update_input_property)

def recommend():
    with driver.session() as session:
        session.write_transaction(update_similarity_property)
        session.write_transaction(update_weight_property)
        session.write_transaction(update_sr_property)
        session.write_transaction(update_recommend_property)
        session.close()

def reset_all_data():
    with driver.session() as session:
        session.write_transaction(delete_adversary_used_edge)
        session.write_transaction(reset_group_property)
        session.write_transaction(reset_technique_property)
        session.write_transaction(reset_used_property)
        session.close()

#Analyze the log to detect techniuqe
def store_file(request_file):
    storage = FileSystemStorage()
    filename = storage.save(str(uuid.uuid1()) + ".csv", request_file)
    path = storage.path(filename)
    return path


def log_parse(log_file):
    with open(os.path.join(settings.CUSTOMISE_FILE_PATH, 'replace_rule.txt'), 'r') as f:
        dictionary_string = f.read()
        replace_rule = ast.literal_eval(dictionary_string)

    special_techniques=[]
    commands_list=[]

    with open(log_file, 'r', encoding='utf-8') as f:
       for line in f:
           if "CommandLine: " in line and "ParentCommandLine: " not in line:
               line = line.replace("CommandLine: ", "")

               #T1059 is the most frequently used technique
               if "powershell.exe" in line or "cmd" in line:
                   line=line.replace("powershell.exe","")
                   if "T1059" not in special_techniques:
                        special_techniques.append("T1059")

               for pattern, replacement in replace_rule.items():
                   line = re.sub(pattern, replacement, line)

               if line not in commands_list:
                    commands_list.append(line.strip())

    return special_techniques, commands_list


def get_techniques(special_techniques, commands_list):
    technique_id_set = set()
    for command in commands_list:
        match_records = Commands.objects.using("attack").filter(command__icontains=command).all()
        for record in match_records:
            technique_id_set.add(record.technique_id)
    
    results=Techniques.objects.using("attack").filter(id__in=list(technique_id_set))
    techniques=[r.external_id for r in results]
    detected_techniques=list(set([technique.split(".")[0] for technique in techniques]))

    for st in special_techniques:
        detected_techniques.append(st)
    
    return detected_techniques


def upload(request):
    if request.method == 'POST' and 'file' in request.FILES and request.FILES['file']:
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['file']
            file_path = store_file(csv_file)
            special_techniques,commands_list=log_parse(file_path)
            detected_techniques=get_techniques(special_techniques,commands_list)
            os.remove(file_path)

            if len(detected_techniques)!=0:
                reset_all_data()
                make_adversary(detected_techniques)
                recommend()
                return redirect(visualize)
            else:
                return render(request,'attck_recommender/unpredictable.html',{"message":"Unpredictable because of no attacks"}) 

        else:
            return HttpResponse('<h1>This is not a csv file.</h1>')

    else:
        return render(request,'attck_recommender/upload.html') 


#Show atomics and search query of SIEM corresponding to the forecasted technique
def search_siem(request):
    with open(os.path.join(settings.CUSTOMISE_FILE_PATH, 'siem_queries.txt'), 'r') as f:
        dictionary_string = f.read()
        siem_queries = ast.literal_eval(dictionary_string)

    with driver.session() as session:
        result=session.read_transaction(get_recommended_techniques)
   
    techniques=[r for r in result]
    if len(techniques)!=0:
        queries={}

        for technique_dic in techniques:
            technique=technique_dic["name"]
            tids=Techniques.objects.using("attack").filter(external_id__contains=technique).values_list('id',flat=True)
            commands_list=[]
            queries_list=[]
            for tid in tids:
                commands=Commands.objects.using("attack").filter(technique_id=tid).values_list('command', flat=True)
                if len(commands)!=0:
                    commands_list.append(list(commands))
            
            if technique in siem_queries:
                queries_list.append(siem_queries[technique])

            queries[(technique, technique_dic["value"])]=[commands_list,queries_list]
        
        context={'queries':queries}
        return render(request,'attck_recommender/search_siem.html',context) 
    else:
        return render(request,'attck_recommender/unpredictable.html',{"message":"Unpredictable because of no attacks"}) 

#Visualize the forecasted results
def visualize(request):
    #Start session, run queries, and get nodes and edges
    with driver.session() as session:
        techniques_result = session.run('MATCH (ta:Tactic)-[c:CONTAINS]->(t:Technique) '
                              'WHERE t.recommend=1 OR t.input=1 '
                              'RETURN ta,c,t')
        
        tactics_result = session.run('MATCH (pre_ta:Tactic)-[n:NEXT]->(nxt_ta:Tactic) '
                                     'RETURN pre_ta, nxt_ta, n')

        nodes, edges = [], []
        for record in techniques_result:
            #Process node data
            tactic_node = record['ta']
            technique_node = record['t']
            technique_node_dict = {'id': technique_node.id, 'label': technique_node['name']}
            if technique_node['recommend'] == 1:
                technique_node_dict['group'] = 'recommended_techniques'
            elif technique_node['input'] == 1:
                technique_node_dict['group'] = 'inputted_techniques'
            nodes.append(technique_node_dict)

            #Process edge data
            contains_edge = record['c']
            edge_dict = {'id': contains_edge.id, 'from': tactic_node.id, 'to': technique_node.id,
                         'label': contains_edge.type, 'arrows': 'to', 'length': '200', 'group': 'contains'}
            edges.append(edge_dict)

        for record in tactics_result:
            #Process node data
            tactic_node = record['pre_ta']
            tactic_node_dict = {'id': tactic_node.id, 'label': tactic_node['name'], 'group': 'tactics'}
            nodes.append(tactic_node_dict)

            next_tactic_node = record['nxt_ta']
            next_tactic_node_dict = {'id': next_tactic_node.id, 'label': next_tactic_node['name'], 'group': 'tactics'}
            nodes.append(next_tactic_node_dict)

            #Process edge data
            next_edge = record['n']
            edge_dict = {'id': next_edge.id, 'from': tactic_node.id, 'to': next_tactic_node.id,
                         'label': next_edge.type, 'arrows': 'to', 'length': '500', 'group': 'next'}
            edges.append(edge_dict)

    #Convert node and edge data to JSON format
    nodes = [dict(t) for t in {tuple(d.items()) for d in nodes}]
    edges = [dict(t) for t in {tuple(d.items()) for d in edges}]

    if len(nodes)!=0:
        context = {
            'nodes': json.dumps(nodes),
            'edges': json.dumps(edges),
        }
        return render(request, 'attck_recommender/visualize.html', context)
    else:
        return render(request,'attck_recommender/unpredictable.html',{"message":"Unpredictable because of no attacks"}) 
    
