import unittest
from aplicacion_ventas.gestos_ventas import GestorVentas
from aplicacion_ventas.exceptions import ImpuestoInvalidoError, DescuentoInvalidoError


class TestGestorVentas(unittest.TestCase):
    
    def test_calculo_precio_final(self):
        gestor = GestorVentas(100.0,0.05,0.10)
        self.assertEqual(gestor.calcular_precio_final(),95.0) # assertEqual es para ver si los valores (gestor y calcular_precio_final) son iguales, si no son iguales, sale error
    
    def test_impuesto_invalido(self):
        with self.assertRaises(ImpuestoInvalidoError): # assertRaises para validar que el codigo maneja los errores y ver si se esta validando de forma correcta
            GestorVentas(100.0,1.5,0.10)
    
    def test_descuento_invalido(self):
        with self.assertRaises(DescuentoInvalidoError):
            GestorVentas(100.0,0.05,1.5)

if __name__=="__main__":
    unittest.main()