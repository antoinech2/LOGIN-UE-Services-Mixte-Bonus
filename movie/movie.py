from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response
import os

import resolvers as r

PORT = 3001
HOST = '0.0.0.0'
app = Flask(__name__)

dirname = os.path.dirname(__file__)

type_defs = load_schema_from_path(f'{dirname}/movie.graphql')
query = QueryType()
movie = ObjectType('Movie')
query.set_field('movie_with_id', r.movie_with_id)
query.set_field('movie_with_title', r.movie_with_title)

mutation = MutationType()
mutation.set_field('update_movie_rate', r.update_movie_rate)

actor = ObjectType('Actor')
movie.set_field('actors', r.resolve_actors_in_movie)

schema = make_executable_schema(type_defs, movie, query, mutation, actor)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    print(data)
    success, result = graphql_sync(
                        schema,
                        data,
                        context_value=None,
                        debug=app.debug
                    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)