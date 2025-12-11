from django.contrib import messages
from django.db.models import Q
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Sum, F, DecimalField, IntegerField, Value, ExpressionWrapper
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation
from django.db.models import Prefetch

def home(request):
    return render(request, "home.html")

def autor_create(request):
    errors = {}
    data = {"nombre": "", "apellido": ""}

    if request.method == "POST":
        data["nombre"] = (request.POST.get("nombre") or "").strip()
        data["apellido"] = (request.POST.get("apellido") or "").strip()

        if not data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        elif len(data["nombre"]) > 80:
            errors["nombre"] = "Máximo 80 caracteres."

        if not data["apellido"]:
            errors["apellido"] = "El apellido es obligatorio."
        elif len(data["apellido"]) > 80:
            errors["apellido"] = "Máximo 80 caracteres."

        
        if not errors and Autor.objects.filter(
            nombre__iexact=data["nombre"],
            apellido__iexact=data["apellido"]
        ).exists():
            errors["general"] = "Ese autor ya existe."

        if not errors:
            Autor.objects.create(nombre=data["nombre"], apellido=data["apellido"])
            messages.success(request, "Autor cargado correctamente.")
            return redirect("autor_list")

    return render(request, "autores/crear.html", {"errors": errors, "data": data})

def autor_list(request):
    autores = Autor.objects.order_by("apellido", "nombre")
    return render(request, "autores/listar.html", {"autores": autores})


def autor_editar(request, id):
    autor = get_object_or_404(Autor, id=id)
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        if nombre and apellido:
            autor.nombre = nombre
            autor.apellido = apellido
            autor.save()
            messages.success(request, "Autor actualizado correctamente.")
            return redirect("autor_list")    
        else:
            messages.error(request, "Todos los campos son obligatorios.")
    return render(request, "autores/editar.html", {"autor": autor})


def autor_eliminar(request, id):
    autor = get_object_or_404(Autor, id=id)
    if request.method == "POST":
        autor.delete()
        messages.success(request, "Autor eliminado correctamente.")
        return redirect("autor_list")  
    autor = get_object_or_404(Autor, id=id)
    if request.method == "POST":
        autor.delete()
        messages.success(request, "Autor eliminado correctamente.")
        return redirect("autor_create")
    return redirect("autor_create")

def categoria_create(request):
    errors = {}
    data = {"nombre": ""}

    if request.method == "POST":
        data["nombre"] = (request.POST.get("nombre") or "").strip()

        if not data["nombre"]:
            errors["nombre"] = "El nombre es obligatorio."
        elif len(data["nombre"]) > 80:
            errors["nombre"] = "Máximo 80 caracteres."

        if not errors and Categoria.objects.filter(nombre__iexact=data["nombre"]).exists():
            errors["general"] = "Esa categoría ya existe."

        if not errors:
            Categoria.objects.create(nombre=data["nombre"])
            messages.success(request, "Categoría creada correctamente.")
            return redirect("categoria_list")

    return render(request, "categorias/crear.html", {"errors": errors, "data": data})


def categoria_list(request):
    categorias = Categoria.objects.order_by("nombre")
    return render(request, "categorias/listar.html", {"categorias": categorias})


def categoria_editar(request, id):
    cat = get_object_or_404(Categoria, id=id)
    errors = {}

    if request.method == "POST":
        nombre = (request.POST.get("nombre") or "").strip()

        if not nombre:
            errors["nombre"] = "El nombre es obligatorio."
        elif len(nombre) > 80:
            errors["nombre"] = "Máximo 80 caracteres."
        elif Categoria.objects.filter(nombre__iexact=nombre).exclude(id=cat.id).exists():
            errors["nombre"] = "Ya existe otra categoría con ese nombre."

        if not errors:
            cat.nombre = nombre
            cat.save()
            messages.success(request, "Categoría actualizada correctamente.")
            return redirect("categoria_list")

    return render(request, "categorias/editar.html", {"cat": cat, "errors": errors})


def categoria_eliminar(request, id):
    cat = get_object_or_404(Categoria, id=id)
    if request.method == "POST":
        cat.delete()
        messages.success(request, "Categoría eliminada correctamente.")
        return redirect("categoria_list")
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == "POST":
        categoria.delete()
        messages.success(request, "Categoría eliminada correctamente.")
    return redirect("categoria_create")



def libros_list(request):
    libros = (
        Libro.objects
        .select_related("categoria")
        .prefetch_related("autores")
        .order_by("titulo")
    )
    return render(request, "libros/listar.html", {"libros": libros})

def libros_create(request):
    errors = {}
    data = {
        "titulo": "",
        "precio": "",
        "stock": "",
        "categoria_id": "",
        "autores_ids": [],  
    }

    categorias = Categoria.objects.order_by("nombre")
    autores = Autor.objects.order_by("apellido", "nombre")

    if request.method == "POST":
        data["titulo"] = (request.POST.get("titulo") or "").strip()
        data["precio"] = (request.POST.get("precio") or "").strip()
        data["stock"] = (request.POST.get("stock") or "").strip()
        data["categoria_id"] = (request.POST.get("categoria_id") or "").strip()
        data["autores_ids"] = request.POST.getlist("autores_ids")

        if not data["titulo"]:
            errors["titulo"] = "El título es obligatorio."

        try:
            precio_dec = Decimal(data["precio"])
            if precio_dec < 0:
                errors["precio"] = "El precio no puede ser negativo."
        except (InvalidOperation, ValueError):
            errors["precio"] = "Precio inválido. Usá punto decimal (ej: 1999.90)."

        try:
            stock_int = int(data["stock"])
            if stock_int < 0:
                errors["stock"] = "El stock no puede ser negativo."
        except (TypeError, ValueError):
            errors["stock"] = "Stock inválido. Debe ser un entero."

        categoria_obj = None
        if not data["categoria_id"]:
            errors["categoria_id"] = "Seleccioná una categoría."
        else:
            try:
                categoria_obj = Categoria.objects.get(id=int(data["categoria_id"]))
            except (Categoria.DoesNotExist, ValueError):
                errors["categoria_id"] = "Categoría inválida."

        if not data["autores_ids"]:
             errors["autores_ids"] = "Seleccioná al menos un autor."

        if not errors and Libro.objects.filter(titulo__iexact=data["titulo"]).exists():
            errors["general"] = "Ya existe un libro con ese título."

        if not errors:
            libro = Libro.objects.create(
                titulo=data["titulo"],
                precio=precio_dec,
                stock=stock_int,
                categoria=categoria_obj,
            )
            if data["autores_ids"]:
                try:
                    libro.autores.set(Autor.objects.filter(id__in=[int(i) for i in data["autores_ids"]]))
                except ValueError:
                    pass
            messages.success(request, "Libro creado correctamente.")
            return redirect("libros_list")

    return render(
        request,
        "libros/crear.html",
        {"errors": errors, "data": data, "categorias": categorias, "autores": autores},
    )

def libros_editar(request, id):
    libro = get_object_or_404(
        Libro.objects.select_related("categoria").prefetch_related("autores"), id=id
    )
    categorias = Categoria.objects.order_by("nombre")
    autores = Autor.objects.order_by("apellido", "nombre")

    errors = {}
    if request.method == "POST":
        titulo = (request.POST.get("titulo") or "").strip()
        precio_raw = (request.POST.get("precio") or "").strip()
        stock_raw = (request.POST.get("stock") or "").strip()
        categoria_id = (request.POST.get("categoria_id") or "").strip()
        autores_ids = request.POST.getlist("autores_ids")

        if not titulo:
            errors["titulo"] = "El título es obligatorio."

        try:
            precio_dec = Decimal(precio_raw)
            if precio_dec < 0:
                errors["precio"] = "El precio no puede ser negativo."
        except (InvalidOperation, ValueError):
            errors["precio"] = "Precio inválido."

        try:
            stock_int = int(stock_raw)
            if stock_int < 0:
                errors["stock"] = "El stock no puede ser negativo."
        except (TypeError, ValueError):
            errors["stock"] = "Stock inválido."

        categoria_obj = None
        if not categoria_id:
            errors["categoria_id"] = "Seleccioná una categoría."
        else:
            try:
                categoria_obj = Categoria.objects.get(id=int(categoria_id))
            except (Categoria.DoesNotExist, ValueError):
                errors["categoria_id"] = "Categoría inválida."

        if not errors and Libro.objects.filter(titulo__iexact=titulo).exclude(id=libro.id).exists():
            errors["general"] = "Ya existe otro libro con ese título."

        if not errors:
            libro.titulo = titulo
            libro.precio = precio_dec
            libro.stock = stock_int
            libro.categoria = categoria_obj
            libro.save()

            try:
                libro.autores.set(Autor.objects.filter(id__in=[int(i) for i in autores_ids]))
            except ValueError:
                libro.autores.clear()

            messages.success(request, "Libro actualizado correctamente.")
            return redirect("libros_list")

        data = {
            "titulo": titulo,
            "precio": precio_raw,
            "stock": stock_raw,
            "categoria_id": categoria_id,
            "autores_ids": autores_ids,
        }
    else:
        data = {
            "titulo": libro.titulo,
            "precio": str(libro.precio),
            "stock": str(libro.stock),
            "categoria_id": str(libro.categoria.id) if libro.categoria_id else "",
            "autores_ids": [str(a.id) for a in libro.autores.all()],
        }

    return render(
        request,
        "libros/editar.html",
        {"libro": libro, "errors": errors, "data": data, "categorias": categorias, "autores": autores},
    )

def libros_eliminar(request, id):
    libro = get_object_or_404(Libro, id=id)
    if request.method == "POST":
        libro.delete()
        messages.success(request, "Libro eliminado correctamente.")
        return redirect("libros_list")
    libro = get_object_or_404(Libro, id=id)
    if request.method == "POST":
        libro.delete()
        messages.success(request, "Libro eliminado correctamente.")
    return redirect("libros_create")


def ventas_list(request):
    ventas = (
        Venta.objects
        .prefetch_related(Prefetch("detalles", queryset=DetalleVenta.objects.select_related("libro")))
        .order_by("-fecha", "-id")
    )
    return render(request, "ventas/listar.html", {"ventas": ventas})


def ventas_create(request):
    errors = {}
    item_errors = []   
    libros = Libro.objects.order_by("titulo")

    data = {"fecha": "", "items": []} 

    if request.method == "POST":
        data["fecha"] = (request.POST.get("fecha") or "").strip()
        libro_ids = request.POST.getlist("libro_id[]")
        cantidades = request.POST.getlist("cantidad[]")

        items = []
        for lid, qty in zip(libro_ids, cantidades):
            lid = (lid or "").strip()
            qty = (qty or "").strip()
            if not lid and not qty:
                continue
            items.append({"libro_id": lid, "cantidad": qty})
        data["items"] = items

        if not data["fecha"]:
            errors["fecha"] = "La fecha es obligatoria."
        if not items:
            errors["items"] = "Agregá al menos un libro a la venta."

        seen = set()
        clean_items = []   
        for i, it in enumerate(items, start=1):
            lid_txt = it.get("libro_id") or ""
            qty_txt = it.get("cantidad") or ""

            libro = None
            try:
                lid = int(lid_txt)
                libro = Libro.objects.filter(id=lid).first()
                if not libro:
                    item_errors.append(f"Fila {i}: libro inválido.")
                elif lid in seen:
                    item_errors.append(f"Fila {i}: el mismo libro ya fue agregado.")
                else:
                    seen.add(lid)
            except ValueError:
                item_errors.append(f"Fila {i}: libro inválido.")

            cantidad = None
            try:
                cantidad = int(qty_txt)
                if cantidad <= 0:
                    item_errors.append(f"Fila {i}: la cantidad debe ser mayor a 0.")
            except (TypeError, ValueError):
                item_errors.append(f"Fila {i}: la cantidad debe ser un entero.")

            if libro and isinstance(cantidad, int):
                clean_items.append((libro, cantidad, i))

        if not errors and not item_errors:
            with transaction.atomic():
                ids = [lb.id for (lb, _, _) in clean_items]
                libros_locked = (
                    Libro.objects.select_for_update()
                    .filter(id__in=ids)
                    .in_bulk()
                )

                for (lb, qty, i) in clean_items:
                    actual = libros_locked[lb.id].stock
                    if qty > actual:
                        item_errors.append(f"Fila {i}: stock insuficiente. Disponible: {actual}.")

                if not item_errors:
                    venta = Venta.objects.create(fecha=data["fecha"])
                    DetalleVenta.objects.bulk_create([
                        DetalleVenta(venta=venta, libro=lb, cantidad=qty)
                        for (lb, qty, _) in clean_items
                    ])

                    for (lb, qty, _) in clean_items:
                        libros_locked[lb.id].stock -= qty
                    Libro.objects.bulk_update(list(libros_locked.values()), ["stock"])

                    messages.success(request, "Venta registrada correctamente.")
                    return redirect("ventas_list")

    return render(
        request,
        "ventas/crear.html",
        {
            "errors": errors,
            "item_errors": item_errors,
            "data": data,
            "libros": libros,
        },
    )

def ventas_editar(request, id):
    venta = get_object_or_404(
        Venta.objects.prefetch_related(Prefetch("detalles", queryset=DetalleVenta.objects.select_related("libro"))),
        id=id
    )
    libros = Libro.objects.order_by("titulo")

    data = {
        "fecha": venta.fecha.strftime("%Y-%m-%d"),
        "items": [{"libro_id": str(d.libro_id), "cantidad": str(d.cantidad)} for d in venta.detalles.all()]
    }
    errors = {}
    item_errors = []

    if request.method == "POST":
        data["fecha"] = (request.POST.get("fecha") or "").strip()
        libro_ids = request.POST.getlist("libro_id[]")
        cantidades = request.POST.getlist("cantidad[]")

        items = []
        for lid, qty in zip(libro_ids, cantidades):
            lid = (lid or "").strip()
            qty = (qty or "").strip()
            if not lid and not qty:
                continue
            items.append({"libro_id": lid, "cantidad": qty})
        data["items"] = items

        if not data["fecha"]:
            errors["fecha"] = "La fecha es obligatoria."
        if not items:
            errors["items"] = "Agregá al menos un libro."

        clean_new = []  
        seen = set()
        for i, it in enumerate(items, start=1):
            libro = None
            try:
                lid = int(it.get("libro_id") or "")
                libro = Libro.objects.filter(id=lid).first()
                if not libro:
                    item_errors.append(f"Fila {i}: libro inválido.")
                elif lid in seen:
                    item_errors.append(f"Fila {i}: el mismo libro ya fue agregado.")
                else:
                    seen.add(lid)
            except ValueError:
                item_errors.append(f"Fila {i}: libro inválido.")

            cant = None
            try:
                cant = int(it.get("cantidad") or "")
                if cant <= 0:
                    item_errors.append(f"Fila {i}: la cantidad debe ser > 0.")
            except (TypeError, ValueError):
                item_errors.append(f"Fila {i}: la cantidad debe ser un entero.")

            if libro and isinstance(cant, int):
                clean_new.append((libro, cant, i))

        if not errors and not item_errors:
            with transaction.atomic():
                orig_map = {}
                for d in venta.detalles.select_for_update():  
                    orig_map[d.libro_id] = orig_map.get(d.libro_id, 0) + d.cantidad

                new_map = {}
                for lb, cant, _ in clean_new:
                    new_map[lb.id] = new_map.get(lb.id, 0) + cant

                all_ids = set(orig_map.keys()) | set(new_map.keys())

                libros_locked = Libro.objects.select_for_update().filter(id__in=all_ids).in_bulk()

                for lb_id in all_ids:
                    old = orig_map.get(lb_id, 0)
                    new = new_map.get(lb_id, 0)
                    delta = new - old
                    if delta > 0:
                        disponible = libros_locked[lb_id].stock
                        if delta > disponible:
                            item_errors.append(
                                f"Stock insuficiente para '{libros_locked[lb_id].titulo}'. Disponible: {disponible}, requerido extra: {delta}."
                            )

                if not item_errors:
                    venta.fecha = data["fecha"]
                    venta.save()

                    to_delete = [lb_id for lb_id in orig_map.keys() if lb_id not in new_map]
                    if to_delete:
                        DetalleVenta.objects.filter(venta=venta, libro_id__in=to_delete).delete()

                    current = {d.libro_id: d for d in DetalleVenta.objects.filter(venta=venta)}
                    for lb, cant, _ in clean_new:
                        if lb.id in current:
                            d = current[lb.id]
                            d.cantidad = cant
                            d.save(update_fields=["cantidad"])
                        else:
                            DetalleVenta.objects.create(venta=venta, libro=lb, cantidad=cant)

                    for lb_id in all_ids:
                        old = orig_map.get(lb_id, 0)
                        new = new_map.get(lb_id, 0)
                        delta = new - old
                        if delta != 0:
                            libros_locked[lb_id].stock -= delta   
                    Libro.objects.bulk_update(list(libros_locked.values()), ["stock"])

                    messages.success(request, "Venta actualizada correctamente.")
                    return redirect("ventas_list")

    return render(
        request,
        "ventas/editar.html",
        {"venta": venta, "libros": libros, "data": data, "errors": errors, "item_errors": item_errors},
    )

def ventas_eliminar(request, id):
    venta = get_object_or_404(
        Venta.objects.prefetch_related("detalles"),
        id=id
    )
    if request.method == "POST":
        with transaction.atomic():
            ids = list(venta.detalles.values_list("libro_id", flat=True))
            libros_locked = Libro.objects.select_for_update().filter(id__in=ids).in_bulk()

            for d in venta.detalles.all():
                libros_locked[d.libro_id].stock += d.cantidad
            if libros_locked:
                Libro.objects.bulk_update(list(libros_locked.values()), ["stock"])

            DetalleVenta.objects.filter(venta=venta).delete()
            venta.delete()

        messages.success(request, "Venta eliminada y stock restaurado.")
    return redirect("ventas_list")



def reporte_ventas_por_libro(request):
    qs = (
        DetalleVenta.objects
        .select_related("libro")
        .values("libro_id", "libro__titulo")
        .annotate(
            unidades=Sum("cantidad"),
            importe=Sum(
                F("cantidad") * F("libro__precio"),
                output_field=DecimalField(max_digits=14, decimal_places=2)
            ),
        )
        .order_by("libro__titulo")
    )

    totales = qs.aggregate(
        total_unidades=Sum("unidades"),
        total_importe=Sum("importe"),
    )

    return render(
        request,
        "reportes/ventas_por_libro.html",
        {"rows": qs, "totales": totales, "es_preciso": True},
    )

def reporte_ranking_libros(request):
    qs = (
        DetalleVenta.objects
        .select_related("libro")
        .values("libro_id", "libro__titulo", "libro__precio", "libro__stock")
        .annotate(
            unidades=Sum("cantidad"),
            importe=Sum(
                F("cantidad") * F("libro__precio"),
                output_field=DecimalField(max_digits=14, decimal_places=2)
            ),
        )
        .order_by("-unidades", "libro__titulo")
    )

    total_unidades = qs.aggregate(total=Sum("unidades"))["total"] or 0

    rows = []
    for r in qs:
        pct = (r["unidades"] / total_unidades * 100) if total_unidades else 0
        r["porcentaje"] = pct
        rows.append(r)

    return render(
        request,
        "reportes/ranking_libros.html",
        {"rows": rows, "total_unidades": total_unidades},
    )

def reporte_libros_mas_vendidos(request):


    importe_expr = ExpressionWrapper(
        F("detalles_venta__cantidad") * F("precio"),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    libros = (
        Libro.objects
        .annotate(
            unidades_vendidas=Coalesce(
                Sum("detalles_venta__cantidad", output_field=IntegerField()),
                Value(0, output_field=IntegerField())
            ),
            importe_total=Coalesce(
                Sum(importe_expr, output_field=DecimalField(max_digits=14, decimal_places=2)),
                Value(Decimal("0.00"), output_field=DecimalField(max_digits=14, decimal_places=2)),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
        )
        .order_by("-unidades_vendidas", "titulo")
    )

    total_vendidos = libros.aggregate(
        total=Sum("unidades_vendidas", output_field=IntegerField())
    )["total"] or 0

    return render(
        request,
        "reportes/libros_mas_vendidos.html",
        {"libros": libros, "total_vendidos": total_vendidos},
    )