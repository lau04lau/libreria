class libro:
    def __init__(self, id, titulo, precio, stock):
        self.id=id
        self.titulo=titulo
        self.precio=precio
        self.stock=stock

    def __str__(self):
        return "titulo {self.titulo} \nprecio: {self.precio}"