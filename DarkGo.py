#!/usr/bin/env python
# -*- coding: utf-8 -*-     
# Copyright (c) 2017 cyj <chenyijiethu@gmail.com>
# Date: 17-9-18
import os
import re
import time
from multiprocessing import Process, Queue

import flask_restful as restful
import pexpect
from flask import current_app
from flask_restful import reqparse

pattern = re.compile(r'[A-Z] \d\d?', re.M)
POST_HEADERS = {'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'x-requested-with,content-type'}
GET_HEADERS = {'Access-Control-Allow-Origin': '*',
               'Access-Control-Allow-Methods': 'GET',
               'Access-Control-Allow-Headers': 'x-requested-with,content-type'
               }
STR = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
sgf_str = 'abcdefghijklmnopqrstuvwxyz'


def log(message):
    f = open('log.txt', 'a')
    f.write(message + '\n')
    f.close()


def game(game_id, q):
    # Create a New Thread To Run DarkGo
    process = pexpect.spawn('./darknet go test ./go.test.cfg ./go.weights', timeout=100)

    try:
        while True:
            # Waiting the message in Queue
            try:
                time.sleep(0.5)
                value = q.get(False)
            except BaseException as e:
                time.sleep(0.5)
                # print('DarkNet is Waitting...')
                continue

            # Get the Expected Output
            process.expect('1:')
            # print(os.getpid(), process.buffer.decode('utf-8'))

            log(str(os.getpid()) + value)
            # Send the position to the DarkGo
            process.sendline(value)

            # .. Get Output
            process.expect('1:')
            first_choose = pattern.findall(process.buffer.decode('utf-8'))
            #  first_choose is the Result
            # e.g. first_choose == "D 5"

            # print(first_choose[0])

            # Send it Back to the Main Thread
            q.put(first_choose[0])

            # Tell DarkGo to Really Drop the Piece
            process.sendline('1')
    except pexpect.TIMEOUT:
        return


class DarkGO(restful.Resource):
    def post(self):
        parse = reqparse.RequestParser()

        parse.add_argument('msg', type=str)
        parse.add_argument('game_id', type=str, required=True)

        args = parse.parse_args()
        game_id = args["game_id"]
        if not current_app.config["gamepool"].get(game_id):
            return {"message": "game not exists!"}, 200, POST_HEADERS
        q = current_app.config["queuepool"].get(game_id)

        moves = args["msg"].split(';')
        del moves[len(moves) - 1]
        move = moves[len(moves) - 1]
        print(move)
        x = sgf_str.find(move[2])
        y = sgf_str.find(move[3])

        pos_send = STR[int(x)] + ' ' + str(19 - y)
        q.put(pos_send)

        # Waiting the Sub Thread to return the Result
        time.sleep(1)
        while True:
            try:
                time.sleep(0.1)
                value = q.get(False)
                # print('Flask get Result______________________')
                posmsg = value.split(' ')
                x = STR.find(posmsg[0])
                y = 19 - int(posmsg[1])
                return {
                           "msg": args["msg"] + 'W[' + sgf_str[x] + sgf_str[y] + '];',
                           "game_id": game_id
                       }, 200, POST_HEADERS
            except BaseException:
                # print('Flask is Waitting...')
                continue

    def get(self):
        parse = reqparse.RequestParser()
        parse.add_argument('game_id', type=str, required=True)
        args = parse.parse_args()
        game_id = args["game_id"]

        if self.__create_new_game(game_id):

            return {"message": "New game Create!"}, 200, GET_HEADERS
        else:
            return {"message": "game_id exists!"}, 200, GET_HEADERS

    @staticmethod
    def __create_new_game(game_id):
        if not current_app.config["gamepool"].get(game_id):
            q = Queue()
            pw = Process(target=game, args=(game_id, q,))

            # Save the Status Globally
            current_app.config["gamepool"][game_id] = pw
            current_app.config["queuepool"][game_id] = q

            # Start New Thread
            pw.start()
            return True
        else:
            return False
