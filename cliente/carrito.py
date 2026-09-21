from decimal import Decimal
from .models import Producto

class Carrito:
    def __init__(self, request):
        """
        Inicializa el carrito utilizando la sesión HTTP del usuario.
        """
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            # Si no existe carrito en la sesión, se crea un diccionario vacío
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        """
        Agrega un producto al carrito o incrementa la cantidad si ya existe.
        """
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': 0,
                'imagen': producto.imagen.url if producto.imagen else '/static/cliente/img/placeholder.jpg'
            }
        
        self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar()

    def restar(self, producto):
        """
        Resta una unidad del producto. Si llega a cero, se elimina del carrito.
        """
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] -= 1
            if self.carrito[producto_id]['cantidad'] <= 0:
                self.eliminar(producto)
            else:
                self.guardar()

    def eliminar(self, producto):
        """
        Elimina completamente un producto del carrito.
        """
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def guardar(self):
        """
        Notifica a Django que la sesión ha sido modificada para que se guarde.
        """
        self.session.modified = True

    def limpiar(self):
        """
        Vacía completamente el carrito.
        """
        self.session['carrito'] = {}
        self.guardar()

    def obtener_modalidad_entrega(self):
        """Obtiene la modalidad elegida por el cliente."""
        return self.session.get('modalidad_entrega', 'RETIRO')

    def establecer_modalidad_entrega(self, modalidad):
        """Guarda la modalidad de entrega elegida por el cliente."""
        if modalidad not in ('RETIRO', 'DELIVERY'):
            modalidad = 'RETIRO'
        self.session['modalidad_entrega'] = modalidad
        self.guardar()

    def obtener_total_unidades(self):
        """
        Calcula la suma total de ítems individuales en el carrito.
        """
        return sum(item['cantidad'] for item in self.carrito.values())

    def obtener_precio_total(self):
        """
        Calcula el monto monetario total acumulado del carrito.
        """
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())

    def __iter__(self):
        """
        Iterador para recorrer los ítems del carrito y calcular sus subtotales.
        """
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=producto_ids)
        carrito_copia = self.carrito.copy()

        for item in carrito_copia.values():
            item['precio_decimal'] = Decimal(item['precio'])
            item['subtotal'] = item['precio_decimal'] * item['cantidad']
            yield item