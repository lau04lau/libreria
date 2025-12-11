from django.test import TestCase
from django.urls import reverse
from administracion.models import Categoria, Autor, Libro, Venta, DetalleVenta


class VentaCreateTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Fantasía")
        self.autor = Autor.objects.create(nombre="J.K.", apellido="Rowling")
        self.libro = Libro.objects.create(
            titulo="Harry Potter y la piedra filosofal",
            categoria=self.categoria,
            precio=100.00,
            stock=10
        )
        self.libro.autores.add(self.autor)

    def test_crear_venta_exitosa_actualiza_stock(self):
        url = reverse("ventas_create")
        data = {
            "fecha": "2025-11-02",
            "libro_id[]": [str(self.libro.id)],
            "cantidad[]": ["3"],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Venta.objects.count(), 1)
        self.assertEqual(DetalleVenta.objects.count(), 1)
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.stock, 7)

    