from pymacapp.new import App

app = App(name="My First App", script="./test/main.py", identifier="com")
app.spec(overwrite=True).build()
