# Endpoint de Programas de Selección Paginados

## Descripción

El endpoint `/api/seleccion/programas-paginados/` permite obtener programas de selección paginados por rango de índices, optimizando el rendimiento al retornar solo los programas que están en el rango especificado, manteniendo el orden cronológico (fecha_creacion ascendente).

## URL del Endpoint

```
GET /api/seleccion/programas-paginados/
```

## Parámetros de Query

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `desde` | integer | Sí | Índice inicial del rango (base 0) |
| `hasta` | integer | Sí | Índice final del rango (base 0) |

## Ejemplos de Uso

### Ejemplo 1: Obtener los primeros 10 programas
```bash
GET /api/seleccion/programas-paginados/?desde=0&hasta=9
```

### Ejemplo 2: Obtener los siguientes 10 programas
```bash
GET /api/seleccion/programas-paginados/?desde=10&hasta=19
```

### Ejemplo 3: Obtener programas del 20 al 29
```bash
GET /api/seleccion/programas-paginados/?desde=20&hasta=29
```

### Ejemplo 4: Obtener solo 5 programas (del 15 al 19)
```bash
GET /api/seleccion/programas-paginados/?desde=15&hasta=19
```

## Respuesta

### Estructura de Respuesta Exitosa (200 OK)

```json
{
    "resultados": [
        {
            "id": 1,
            "estado_programa": "4",
            "fecha_creacion": "2024-01-15T10:30:00Z",
            "fecha_inicio_proceso": "2024-01-15",
            "fecha_termino_proceso": "2024-01-20",
            "observaciones": "Programa de selección normal",
            "numero_programa": 1,
            "estado_programa_label": "Terminado",
            "registrado_por_label": "Juan Pérez",
            "email_registrador": "juan.perez@empresa.com",
            "totales_kilos": {
                "bins_sin_procesar": 0,
                "bins_procesados": 1500.5
            },
            "kilos_porcentaje": {
                "bins_sin_procesar": 0.0,
                "bins_procesados": 100.0
            },
            "condicion_cierre": true,
            "condicion_termino": true,
            "pepa_para_seleccion_length": 25,
            "comercializador": "Empresa ABC"
        }
        // ... más programas
    ],
    "rango": {
        "desde": 0,
        "hasta": 9,
        "total_programas": 50,
        "programas_en_rango": 10
    }
}
```

### Estructura de Respuesta de Error (400 Bad Request)

```json
{
    "error": "Los parámetros 'desde' y 'hasta' son requeridos (números enteros)"
}
```

## Casos de Error

### 1. Parámetros faltantes
```json
{
    "error": "Los parámetros 'desde' y 'hasta' son requeridos (números enteros)"
}
```

### 2. Parámetros no numéricos
```json
{
    "error": "Los parámetros 'desde' y 'hasta' deben ser números enteros"
}
```

### 3. Índice negativo
```json
{
    "error": "El parámetro 'desde' debe ser mayor o igual a 0"
}
```

### 4. Rango inválido
```json
{
    "error": "El parámetro 'hasta' debe ser mayor o igual a 'desde'"
}
```

### 5. Índice fuera de rango
```json
{
    "error": "El índice 'desde' (100) excede el total de programas disponibles (50)"
}
```

## Características del Endpoint

### Ordenamiento
- Los programas se ordenan por `fecha_creacion` en orden ascendente (más antiguos primero)
- Este orden se mantiene consistente en todas las consultas

### Filtros de Usuario
- El endpoint respeta los filtros de año configurados en el perfil del usuario
- Si el usuario tiene configurado un año específico, solo se retornan programas de ese año
- Si el usuario tiene configurado "Todo", se retornan todos los programas

### Optimización de Rendimiento
- Solo se consultan los registros en el rango especificado
- No se cargan todos los programas en memoria
- La paginación se realiza a nivel de base de datos

### Validaciones
- Validación de tipos de datos (números enteros)
- Validación de rangos (desde ≤ hasta)
- Validación de límites (no exceder el total de programas)
- Ajuste automático del índice "hasta" si excede el total

## Implementación en el Frontend

### Ejemplo con JavaScript/Fetch

```javascript
async function obtenerProgramasPaginados(desde, hasta) {
    try {
        const response = await fetch(`/api/seleccion/programas-paginados/?desde=${desde}&hasta=${hasta}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error al obtener programas:', error);
        throw error;
    }
}

// Ejemplo de uso
const programas = await obtenerProgramasPaginados(0, 9);
console.log(`Programas del 0 al 9: ${programas.resultados.length}`);
console.log(`Total de programas disponibles: ${programas.rango.total_programas}`);
```

### Ejemplo con React

```jsx
import { useState, useEffect } from 'react';

function ProgramasSeleccion() {
    const [programas, setProgramas] = useState([]);
    const [paginaActual, setPaginaActual] = useState(0);
    const [totalProgramas, setTotalProgramas] = useState(0);
    const [cargando, setCargando] = useState(false);
    const programasPorPagina = 10;

    const cargarProgramas = async (desde, hasta) => {
        setCargando(true);
        try {
            const response = await fetch(`/api/seleccion/programas-paginados/?desde=${desde}&hasta=${hasta}`);
            const data = await response.json();
            
            setProgramas(data.resultados);
            setTotalProgramas(data.rango.total_programas);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setCargando(false);
        }
    };

    const cambiarPagina = (nuevaPagina) => {
        const desde = nuevaPagina * programasPorPagina;
        const hasta = desde + programasPorPagina - 1;
        setPaginaActual(nuevaPagina);
        cargarProgramas(desde, hasta);
    };

    useEffect(() => {
        cargarProgramas(0, programasPorPagina - 1);
    }, []);

    return (
        <div>
            {cargando ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <h2>Programas de Selección</h2>
                    <div>
                        {programas.map(programa => (
                            <div key={programa.id}>
                                <h3>Programa {programa.id}</h3>
                                <p>Estado: {programa.estado_programa_label}</p>
                                <p>Fecha: {programa.fecha_creacion}</p>
                            </div>
                        ))}
                    </div>
                    
                    <div>
                        <button 
                            onClick={() => cambiarPagina(paginaActual - 1)}
                            disabled={paginaActual === 0}
                        >
                            Anterior
                        </button>
                        <span>Página {paginaActual + 1}</span>
                        <button 
                            onClick={() => cambiarPagina(paginaActual + 1)}
                            disabled={(paginaActual + 1) * programasPorPagina >= totalProgramas}
                        >
                            Siguiente
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
```

## Notas Importantes

1. **Base 0**: Los índices comienzan en 0, no en 1
2. **Rango Inclusivo**: El parámetro `hasta` es inclusivo (incluye el programa en esa posición)
3. **Orden Cronológico**: Los programas siempre se ordenan por fecha de creación ascendente
4. **Filtros de Usuario**: Se respetan los filtros de año configurados en el perfil
5. **Validación Automática**: El endpoint ajusta automáticamente el rango si excede el total de programas
6. **Optimización**: Solo se consultan los registros necesarios, mejorando el rendimiento 