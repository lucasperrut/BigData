from flask import Flask,jsonify,request
from flask import render_template
import ast

app = Flask(__name__)

hashtags = []
hashtagsCount = []
palavras = []
mencoes = []
palavrasTup = []


@app.route("/")
def chart():
    # global hashtags,hashtagsCount, palavras, mencoes
    global hashtags,hashtagsCount, palavrasTup
    hashtags = []
    hashtagsCount = []
    palavras = []
    mencoes = []
    # return render_template('chart.html', hashtagsCount=hashtagsCount, hashtags=hashtags, palavras=palavras, mencoes=mencoes)
    return render_template('chart.html', hashtagsCount=hashtagsCount, hashtags=hashtags, palavras=palavrasTup)


@app.route('/atualizarDados')
def refresh_graph_data():
    #global hashtags, hashtagsCount, palavras, mencoes
    global hashtags, hashtagsCount, palavrasTup
    print("Tags: " + str(hashtags))
    print("Contador: " + str(hashtagsCount))
    #return jsonify(sLabel=hashtags, sData=hashtagsCount, sPalavras=palavras, sMencoes=mencoes)
    return jsonify(sLabel=hashtags, sData=hashtagsCount, sPalavras=palavrasTup)


@app.route('/atualizarPainel', methods=['POST'])
def update_data_post():
    # global hashtags, hashtagsCount
    global hashtags,hashtagsCount, palavrasTup
    if not request.form or 'data' not in request.form:
        return "error",400
    hashtags = ast.literal_eval(request.form['label'])
    hashtagsCount = ast.literal_eval(request.form['data'])
    #palavras = ast.literal_eval(request.form['palavras'])
    #mencoes = ast.literal_eval(request.form['mencoes'])
    palavrasTup = ast.literal_eval(request.form['palavrasTup'])
    print("Hashtags Recebidas: " + str(hashtags))
    print("Contador: " + str(hashtagsCount))
    #print("Palavras Recebidas: " + str(palavras))
    #print("Mencoes: " + str(mencoes))
    print("PalavrasTup" + str(palavrasTup))
    return "success",201


if __name__ == "__main__":
    app.run(host='localhost', port=5001)

