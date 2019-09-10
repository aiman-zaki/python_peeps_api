from pymongo import MongoClient
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,decode_token,create_refresh_token,jwt_refresh_token_required,
    set_access_cookies,set_refresh_cookies
)
import re
import datetime
import os
import functools
from flask import request , jsonify, json , Response
from flask_cors import CORS
from flask_restful import Resource, Api, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from bson import json_util
from main import db , app 
from bson.json_util import dumps, ObjectId

class Assignments(Resource):
    #@jwt_required
    def put(self): 
        #current_user = get_jwt_identity()
        group_id = request.json['group_id']
        #Security measures i guess?
        """valid = db.users.count_documents({
            '$and':[
                {'email':current_user},
                {'active_group': group_id}
            ]
        })
        if valid is 0:
            return {'message':'You are not valid to view this'}
        data = db.assignments.find_one({'group_id':ObjectId(group_id)})
        """
        data = db.assignments.aggregate([
            
            {'$match':{'group_id':ObjectId(group_id)}},
            {'$unwind':'$assignments'},
            {
                '$lookup':{
                    'from':'tasks',
                    'localField':'assignments._id',
                    'foreignField':'assignment_id',
                    'as':'tasks',
                }
            },
            {'$unwind':'$tasks'},
            {'$project':
                {
                    '_id':'$assignments._id',
                    'title':'$assignments.title',
                    'description':'$assignments.description',
                    'leader': '$assignments.leader',
                    'totalMarks': '$assignments.totalMarks',
                    'scoredMarks' : '$assignments.scoredMarks',
                    'status':'$assignments.status',
                    'tasks':'$tasks.tasks'
                
                },
              
            
            }
            
        
        ])
        return Response(
            json_util.dumps(data),
            mimetype='application/json'
        )






class Assignment(Resource):
    def put(self):
        #current_user = get_jwt_identity()
        group_id = request.json['group_id']
        assignment_id = request.json['assignment_id']

        data = db.assignments.aggregate(
            [
                {'$match': {
                    '$and':[
                        {'group_id':ObjectId(group_id)},
                        {'assignments._id':ObjectId(assignment_id)}
                    ],
                },},
               {
                   '$project':{
                
                       'assignment':{
                           '$filter':{
                               'input': '$assignments',
                               'as': 'assignment',
                               'cond':{'$eq':['$$assignment._id',ObjectId(assignment_id)]}
                           }
                       }
                   }
               },
               {'$unwind':'$assignment'},
               {'$replaceRoot': { 'newRoot': '$assignment' } }
             
            
            ],
            
        )
        
        json = json_util.dumps(data)

        return Response(
            json,
            mimetype='application/json'
        )
    
    
    def post(self):
        _id = ObjectId()
        current_user = get_jwt_identity()
        group_id = request.json['group_id']
        assignment = request.json['assignment']
        db.assignments.update_one(
            {'group_id':ObjectId(group_id)},
            {'$push':{
                'assignments': {
                    '_id': _id,
                    'title':assignment['title'],
                    'description':assignment['description'],
                    'leader':assignment['leader'],
                    'totalMarks':assignment['totalMarks'],
  
                }
            }}
        )
        db.tasks.insert_one({'assignment_id':_id})



class AddTask(Resource):
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()
        assignment_id = request.json['assignment_id']
        todo = request.json['todo']
        todo['_id'] = ObjectId()
        db.tasks.update_one(
        {
            'assignment_id':ObjectId(assignment_id),
        },
        {
            '$addToSet':{'tasks':todo}
            
        },upsert=True)

        return Response(
            json_util.dumps({
                'message':'message'
            }),
            mimetype='application/json'
        )

class UpdateTask(Resource):
    def post(self):
        pass

    def delete(self,assignment_id,task_id):
        try:
            db.tasks.update_one({
                'assignment_id':ObjectId(assignment_id),
 
            },
            {
                '$pull':{
                    'tasks': {
                        '_id':ObjectId(task_id)
                    }
                }
            })
        except:
            abort(400,message="Cannot Delete")

        return Response(

        )
    
#Used to update task status , delete from old array and push to new
class UpdateTaskStatus(Resource):
    def put(self):
        assignment_id = request.json['assignment_id']
        tasks = request.json['tasks']
        for task in tasks:
            print(task)
            db.tasks.update_one(
                {
             
                    'assignment_id':ObjectId(assignment_id),
                    'tasks._id':ObjectId(task['id'])
            
                },
                {
                    '$set':{
                        'tasks.$.status': task['status']
                    }
                },
            )

        """
        cursorTasks = db.assignments.aggregate([
          {'$match':{
              'group_id': ObjectId(group_id),
          }},
          {'$unwind':'$assignments'},
          {'$match':{'assignments._id': ObjectId(assignment_id)}},
          {'$unwind':'$assignments.tasks'},
          {'$match':{'assignments.tasks._id': {'$in':tasks_id}}},  
          {'$project':
          {
            
              '_id':'$assignments.tasks._id',
              'creator': '$assignments.tasks.creator',
              'assignTo' :'$assignments.tasks.assignTo',
              'task' : '$assignments.tasks.task',
              'description' : '$assignments.tasks.description',
              'createdDate' : '$assignments.tasks.createdDate',
              'assignDate' : '$assignments.tasks.assignDate',
              'dueDate' : '$assignments.tasks.dueDate',
              'lastUpdated' : '$assignments.tasks.lastUpdated',
              'priority' : '$assignments.tasks.priority',
              'status' : '$assignments.tasks.status',
            
          }}
        ])

        tasksJson = json.loads(json_util.dumps(cursorTasks))

        for task in tasks:
            for taskJson in tasksJson:
                if(taskJson['_id']['$oid'] == task['id']):
                    taskJson['status'] = task['status']
        
        """