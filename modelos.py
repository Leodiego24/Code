# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
from sqlalchemy import create_engine
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.model_selection import cross_val_score
import sklearn.naive_bayes
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from matplotlib import pyplot as plt
import numpy as np
from sklearn.tree import export_graphviz
from subprocess import call
import pickle


database = {
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'leogun240594',
        'HOST': 'localhost',
        'PORT': 5432,
    }

engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
    user = database['USER'],
    password = database['PASSWORD'],
    host = database['HOST'],
    port = database['PORT'],
    database = database['NAME'],
)
engine = create_engine(engine_string)

df = pd.read_sql('select * from desertion.vw_ingdata_v2',engine)

df['periodo_anterior'] = df['periodo_anterior'].fillna(0)
df['porcetaje_perdida_materia'] = df['porcetaje_perdida_materia'].fillna(0)
df['aprueba_periodo'] = df['aprueba_periodo'].fillna(0)
df['periodo_anterior'] = df['periodo_anterior'].fillna(0)
df['creditos_aprobados'] = df['creditos_aprobados'].fillna(0)
df['porcetaje_perdida_materia'] = df['porcetaje_perdida_materia'].fillna(0)
df['promedio_acumulado'].fillna(value=df['promedio_acumulado'].mean(), inplace=True)
df['promedio_materia_anterior'].fillna(value=df['promedio_materia_anterior'].mean(), inplace=True)

df = df.dropna(subset=['aprueba_materia'])

def execute_model(df_rg, columns_drop, columns_evaluate, label_columns, x):
    

    df_rg.drop(columns_drop,inplace=True, axis=1)    

    df_rg[columns_evaluate] = preprocessing.StandardScaler().fit_transform(df_rg[columns_evaluate])
    
    lb = LabelEncoder()     
    
    df_rg = df_rg.apply(lambda x: lb.fit_transform(x) if x.name in label_columns else x)
    
    y = df_rg[x]
    X = df_rg.drop(x, axis=1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.15, random_state=0)
    
    names=['naive bayes','decision tree','logistic','randomForest','----']
    models=[sklearn.naive_bayes.GaussianNB(),
                    DecisionTreeClassifier(random_state=0),
                    LogisticRegression(random_state=0,penalty='l2', max_iter=100000),
                    RandomForestClassifier()]
    
    for reg,name in zip(models,names):
        scores = cross_val_score(reg, X_train, y_train.ravel(), scoring='f1',cv=5)
        print('--------------------------------------')
        print('model {0:20} | score {1:20}'.format(name,'f1'))
        print('mean {0:22.2f}| std   {1:<22.2f}'.format(scores.mean(),scores.std()))
        print("Accuracy(95.7%): {0:10.2f} (+/- {1:.2f})" .format(scores.mean(), scores.std() * 2))    
    
    #X = df[['promedio_acumulado','creditos_aprobados']].to_numpy()
    #y = lb.fit_transform(df['aprueba_materia'])

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1212)
    
    #clf = DecisionTreeClassifier().fit(X_train, y_train)
    #fig = plt.figure(figsize=(25,20))
    #_ = tree.plot_tree(clf, 
    #                   feature_names=['promedio_acumulado','creditos_aprobados'],
    #                   class_names=['True', 'False'],
    #                   filled=True)
    #fig.savefig("decistion_tree.svg")

def get_radom_forest(df_rg, columns_drop, columns_evaluate, label_columns, x, pkl_name):
    model = RandomForestClassifier(n_estimators=10)
    df_rg.drop(columns_drop,inplace=True, axis=1)    

    df_rg[columns_evaluate] = preprocessing.StandardScaler().fit_transform(df_rg[columns_evaluate])
    
    lb = LabelEncoder()     
    
    df_rg = df_rg.apply(lambda x: lb.fit_transform(x) if x.name in label_columns else x)
    
    y = df_rg[x]
    X = df_rg.drop(x, axis=1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.15, random_state=0)
    model.fit(X_train, y_train)
    # estimator = model.estimators_[5]
    
    # export_graphviz(estimator, out_file='tree_1.dot',
    #             rounded = True, proportion = False, 
    #             precision = 3, filled = True)
    
    # estimator = model.estimators_[1]
    
    # export_graphviz(estimator, out_file='tree_2.dot',
    #             rounded = True, proportion = False, 
    #             precision = 3, filled = True)

    # estimator = model.estimators_[3]
    
    # export_graphviz(estimator, out_file='tree_3.dot',
    #             rounded = True, proportion = False, 
    #             precision = 3, filled = True)
    model.predict(X_train)
    name_file=pkl_name
    myfile = open(name_file, 'wb')
    pickle.dump(model,myfile)
    myfile.close()
    
    #call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])
    
    
columns_drop = ['programa',
                'estudiante',
                'asignatura',
                'periodo',
                'nucleo',
                'origen',
                'nota_mom1',
                'nota_mom2',
                'nota_mom3',
                'definitiva',
                'aprueba_periodo']

columns = ['periodo_anterior',
            'promedio_acumulado', 
            'promedio_materia_anterior',
            'creditos_aprobados',
            'porcetaje_perdida_materia']

label_columns = ['aprueba_materia',
                 'codigo_asig',
                 'codigo']

print('----Probabilidad de perdida materia, sin notas-----')
#execute_model(df.copy(), columns_drop, columns, label_columns, 'aprueba_materia')
get_radom_forest(df.copy(), columns_drop, columns, label_columns, 'aprueba_materia', 'result_1.pkl')
print('---------------------------------------------------')

columns_drop.remove("nota_mom1")
columns.append("nota_mom1")
df = df.dropna(subset=['nota_mom1'])

print('----Probabilidad de perdida materia, primer corte de notas-----')
#execute_model(df.copy(), columns_drop, columns, label_columns, 'aprueba_materia')
get_radom_forest(df.copy(), columns_drop, columns, label_columns, 'aprueba_materia', 'result_2.pkl')
print('---------------------------------------------------')

columns_drop.remove("nota_mom2")
columns.append("nota_mom2")
df = df.dropna(subset=['nota_mom2'])

print('----Probabilidad de perdida materia, primer y segundo corte de notas-----')
get_radom_forest(df.copy(), columns_drop, columns, label_columns, 'aprueba_materia', 'result_3.pkl')
#execute_model(df.copy(), columns_drop, columns, label_columns, 'aprueba_materia')
print('---------------------------------------------------')