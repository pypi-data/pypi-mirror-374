from .descuentos import Descuentos
from .impuestos import Impuestos
from .precios import Precios

class GestorVentas:
    def __init__(self,precio_base,impuestos_porcentaje,descuentos_porcentaje):
        self.precio_base = precio_base
        self.impuestos = Impuestos(impuestos_porcentaje)
        self.descuentos = Descuentos(descuentos_porcentaje)
        
    def calcular_precio_final(self):
        impuestos_aplicados = self.impuestos.aplicar_impuesto(self.precio_base)
        descuentos_aplicados = self.descuentos.aplicar_descuento(self.precio_base)
        precio_final = Precios.calcular_precio_final(self.precio_base,impuestos_aplicados,descuentos_aplicados)
        return round(precio_final)
    
        