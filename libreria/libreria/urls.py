from django.urls import path
from administracion import views as administracion

urlpatterns = [
    path("", administracion.home, name="home"),
    path("autores/", administracion.autor_list, name="autor_list"),
    path("autores/nuevo/", administracion.autor_create, name="autor_create"),
    path("autores/editar/<int:id>/", administracion.autor_editar, name="autor_editar"),
    path("autores/eliminar/<int:id>/", administracion.autor_eliminar, name="autor_eliminar"),
    path("categorias/", administracion.categoria_list, name="categoria_list"),
    path("categorias/nuevo/", administracion.categoria_create, name="categoria_create"),
    path("categorias/editar/<int:id>/", administracion.categoria_editar, name="categoria_editar"),
    path("categorias/eliminar/<int:id>/", administracion.categoria_eliminar, name="categoria_eliminar"),
    path("libros/", administracion.libros_list, name="libros_list"),
    path("libros/nuevo/", administracion.libros_create, name="libros_create"),
    path("libros/editar/<int:id>/", administracion.libros_editar, name="libros_editar"),
    path("libros/eliminar/<int:id>/", administracion.libros_eliminar, name="libros_eliminar"),
    path("ventas/", administracion.ventas_list, name="ventas_list"),
    path("ventas/nuevo/", administracion.ventas_create, name="ventas_create"),
    path("ventas/editar/<int:id>/", administracion.ventas_editar, name="ventas_editar"),
    path("ventas/eliminar/<int:id>/", administracion.ventas_eliminar, name="ventas_eliminar"),
    path("reportes/ventas-por-libro/", administracion.reporte_ventas_por_libro, name="reporte_ventas_por_libro"),
    path("reportes/ranking-libros/", administracion.reporte_ranking_libros, name="reporte_ranking_libros"),
    path("reportes/libros-mas-vendidos/", administracion.reporte_libros_mas_vendidos, name="reporte_libros_mas_vendidos"),
    
]
