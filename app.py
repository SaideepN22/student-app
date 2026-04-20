from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

students = []

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.args.get('search', '').lower()

    if request.method == 'POST':
        name = request.form['name']
        usn = request.form['usn']
        students.append({'name': name, 'usn': usn})

    if search_query:
        filtered_students = [
            s for s in students
            if search_query in s['name'].lower() or search_query in s['usn'].lower()
        ]
    else:
        filtered_students = students

    return render_template(
        'index.html',
        students=filtered_students,
        total=len(students),
        search_query=search_query
    )

@app.route('/delete/<int:index>')
def delete(index):
    if 0 <= index < len(students):
        students.pop(index)
    return redirect(url_for('index'))

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    if request.method == 'POST':
        students[index]['name'] = request.form['name']
        students[index]['usn'] = request.form['usn']
        return redirect(url_for('index'))
    return render_template('edit.html', student=students[index], index=index)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
