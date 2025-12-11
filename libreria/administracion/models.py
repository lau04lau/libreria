from django.db import models
from django.core.validators import MinValueValidator


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)


    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        "Categoria",
        on_delete=models.PROTECT,           
        related_name="libros",
    )
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(default=0)

    autores = models.ManyToManyField(
        "Autor",
        through="AutorLibro",
        related_name="libros",
    )


    def __str__(self):
        return self.titulo


class AutorLibro(models.Model):
    autor = models.ForeignKey("Autor", on_delete=models.CASCADE)
    libro = models.ForeignKey("Libro", on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.autor} → {self.libro}"


class Venta(models.Model):
    fecha = models.DateField()

    
    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha}"

    @property
    def total(self):
        return sum(d.subtotal for d in self.detalles.all())


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        "Venta",
        on_delete=models.CASCADE,           
        related_name="detalles",
    )
    libro = models.ForeignKey(
        "Libro",
        on_delete=models.PROTECT,           
        related_name="detalles_venta",
    )
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.venta} · {self.libro} x {self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.libro.precio
