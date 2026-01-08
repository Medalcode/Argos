"""
Tests para el sistema de memoria (persistencia de estado)
"""
import pytest
import json
import os
import sys
import tempfile
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import memoria


class TestMemoria:
    """Tests para funciones de memoria.py"""
    
    def test_cargar_estado_archivo_no_existe(self):
        """Test que devuelve estado default si archivo no existe"""
        with patch('os.path.exists', return_value=False):
            estado = memoria.cargar_estado()
            
            assert estado["posicion_abierta"] == False, "Posición debe estar cerrada por default"
            assert estado["precio_compra"] == 0, "Precio de compra debe ser 0"
            assert estado["pnl_acumulado"] == 0.0, "PnL debe ser 0"
    
    def test_cargar_estado_archivo_existe(self):
        """Test que carga estado desde archivo JSON"""
        estado_mock = {
            "posicion_abierta": True,
            "precio_compra": 90000,
            "cantidad": 0.01,
            "max_precio": 91000,
            "pnl_acumulado": 5.5
        }
        
        mock_json = json.dumps(estado_mock)
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_json)):
                estado = memoria.cargar_estado()
                
                assert estado["posicion_abierta"] == True, "Debe cargar posición abierta"
                assert estado["precio_compra"] == 90000, "Debe cargar precio correcto"
                assert estado["max_precio"] == 91000, "Debe cargar máximo precio"
    
    def test_cargar_estado_archivo_corrupto(self):
        """Test que maneja archivo JSON corrupto"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="{ invalid json")):
                estado = memoria.cargar_estado()
                
                # Debe devolver estado default
                assert estado["posicion_abierta"] == False, "Debe devolver default si JSON corrupto"
    
    def test_guardar_estado(self):
        """Test que guarda estado correctamente"""
        estado_test = {
            "posicion_abierta": True,
            "precio_compra": 91000,
            "cantidad": 0.015,
            "max_precio": 92000
        }
        
        # Usar archivo temporal real
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            # Guardar con path temporal
            with patch('memoria.ESTADO_FILE', tmp_path):
                memoria.guardar_estado(estado_test)
            
            # Leer y verificar
            with open(tmp_path, 'r') as f:
                estado_cargado = json.load(f)
            
            assert estado_cargado["posicion_abierta"] == True
            assert estado_cargado["precio_compra"] == 91000
            assert estado_cargado["cantidad"] == 0.015
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_estado_persistencia_ciclo_completo(self):
        """Test ciclo completo: guardar y cargar"""
        estado_original = {
            "posicion_abierta": True,
            "precio_compra": 89500,
            "cantidad": 0.02,
            "max_precio": 90000,
            "pnl_acumulado": 3.5,
            "operaciones_hoy": 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name
        
        try:
            # Guardar
            with patch('memoria.ESTADO_FILE', tmp_path):
                memoria.guardar_estado(estado_original)
                
                # Cargar
                with patch('os.path.exists', return_value=True):
                    estado_cargado = memoria.cargar_estado()
            
            # Verificar que son iguales
            assert estado_cargado["posicion_abierta"] == estado_original["posicion_abierta"]
            assert estado_cargado["precio_compra"] == estado_original["precio_compra"]
            assert estado_cargado["cantidad"] == estado_original["cantidad"]
            assert estado_cargado["pnl_acumulado"] == estado_original["pnl_acumulado"]
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
