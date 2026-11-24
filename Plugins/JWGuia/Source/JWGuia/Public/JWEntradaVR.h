// Jatun Wasi Nawpa Kay - tesis VR Quest 2
// UJWEntradaVR: lectura de los controles por ACCIONES de Enhanced Input.
//
// POR QUE: en UE 5.7, si el proyecto define DefaultMappingContexts (Enhanced Input), el plugin OpenXR solo
// construye acciones de Enhanced Input y las INYECTA en las acciones (InjectInputForAction); NO crea las
// acciones "legacy" que actualizan el estado de cada tecla (OpenXRInput.cpp, BuildEnhancedActions vs
// BuildLegacyActions). Resultado en el visor: GetInputAnalogKeyState / WasInputKeyJustPressed de las teclas
// OculusTouch_* devuelven SIEMPRE 0 -> no se podia mover, ni usar el boton A ni el gatillo del pozo.
// Estas funciones leen el valor de las acciones IA_JW_* (mapeadas en IMC_Default), que si llegan.
// Respaldo: si no hay subsistema de Enhanced Input (p.ej. editor sin XR), usan el estado de tecla clasico.
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "JWEntradaVR.generated.h"

UCLASS()
class JWGUIA_API UJWEntradaVR : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Palanca derecha, eje X (-1..1): derecha/izquierda. */
	UFUNCTION(BlueprintPure, Category = "JW Entrada", meta = (WorldContext = "WorldContextObject"))
	static float MoverX(const UObject* WorldContextObject);

	/** Palanca derecha, eje Y (-1..1): adelante/atras. */
	UFUNCTION(BlueprintPure, Category = "JW Entrada", meta = (WorldContext = "WorldContextObject"))
	static float MoverY(const UObject* WorldContextObject);

	/** true solo en el fotograma en que se presiona el boton A (derecho). */
	UFUNCTION(BlueprintPure, Category = "JW Entrada", meta = (WorldContext = "WorldContextObject"))
	static bool BotonAPulsado(const UObject* WorldContextObject);

	/** true solo en el fotograma en que se presiona el gatillo derecho. */
	UFUNCTION(BlueprintPure, Category = "JW Entrada", meta = (WorldContext = "WorldContextObject"))
	static bool GatilloPulsado(const UObject* WorldContextObject);

	/** PRUEBAS (PIE): activa IMC_Default como en el visor e inyecta un valor en la accion IA_JW_<Nombre>
	 *  por la MISMA via que OpenXR (InjectInputForAction). Devuelve false si falta algo. */
	UFUNCTION(BlueprintCallable, Category = "JW Entrada|Pruebas", meta = (WorldContext = "WorldContextObject"))
	static bool PruebaInyectar(const UObject* WorldContextObject, const FString& NombreAccion, FVector Valor);

	/** PRUEBAS (PIE): inyeccion continua (bIniciar=true) o detenerla (false). */
	UFUNCTION(BlueprintCallable, Category = "JW Entrada|Pruebas", meta = (WorldContext = "WorldContextObject"))
	static bool PruebaInyectarContinuo(const UObject* WorldContextObject, const FString& NombreAccion, FVector Valor, bool bIniciar);

	/** Texto de diagnostico con los valores actuales (para pruebas). */
	UFUNCTION(BlueprintCallable, Category = "JW Entrada", meta = (WorldContext = "WorldContextObject"))
	static FString Diagnostico(const UObject* WorldContextObject);
};
