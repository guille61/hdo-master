from master import create_app # Se importa la función de creación de la aplicación

app = create_app()

if __name__ == "__main__":
    app.run(port = "5000", debug = True)
    