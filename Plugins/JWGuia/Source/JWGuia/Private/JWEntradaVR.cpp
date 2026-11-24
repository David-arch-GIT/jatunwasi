// Jatun Wasi Nawpa Kay - lectura de controles por acciones de Enhanced Input (ver JWEntradaVR.h)
#include "JWEntradaVR.h"

#include "Engine/LocalPlayer.h"
#include "Engine/World.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedPlayerInput.h"
#include "GameFramework/PlayerController.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"

namespace JWEntradaVRPrivate
{
	static const TCHAR* RutaMover = TEXT("/Game/JWN/Input/IA_JW_Mover.IA_JW_Mover");
	static const TCHAR* RutaBotonA = TEXT("/Game/JWN/Input/IA_JW_BotonA.IA_JW_BotonA");
	static const TCHAR* RutaGatillo = TEXT("/Game/JWN/Input/IA_JW_Gatillo.IA_JW_Gatillo");

	static const UInputAction* Accion(const TCHAR* Ruta)
	{
		// Carga (una vez) del asset; IMC_Default lo referencia, asi que esta cocinado en el APK.
		static TMap<FString, TWeakObjectPtr<const UInputAction>> Cache;
		if (const TWeakObjectPtr<const UInputAction>* Hit = Cache.Find(Ruta))
		{
			if (Hit->IsValid())
			{
				return Hit->Get();
			}
		}
		const UInputAction* A = LoadObject<UInputAction>(nullptr, Ruta);
		Cache.Add(Ruta, A);
		return A;
	}

	static APlayerController* PC(const UObject* Ctx)
	{
		return Ctx ? UGameplayStatics::GetPlayerController(Ctx, 0) : nullptr;
	}

	static UEnhancedPlayerInput* PlayerInput(const UObject* Ctx)
	{
		APlayerController* P = PC(Ctx);
		if (!P || !P->GetLocalPlayer())
		{
			return nullptr;
		}
		if (UEnhancedInputLocalPlayerSubsystem* S = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(P->GetLocalPlayer()))
		{
			return S->GetPlayerInput();
		}
		return nullptr;
	}

	static FVector2D Mover(const UObject* Ctx)
	{
		FVector2D V = FVector2D::ZeroVector;
		if (UEnhancedPlayerInput* EPI = PlayerInput(Ctx))
		{
			if (const UInputAction* A = Accion(RutaMover))
			{
				V = EPI->GetActionValue(A).Get<FVector2D>();
			}
		}
		// Respaldo (editor/PC): estado de tecla clasico, por si la accion no da nada.
		if (V.IsNearlyZero())
		{
			if (APlayerController* P = PC(Ctx))
			{
				const FVector2D K(P->GetInputAnalogKeyState(FKey(TEXT("OculusTouch_Right_Thumbstick_X"))),
				                  P->GetInputAnalogKeyState(FKey(TEXT("OculusTouch_Right_Thumbstick_Y"))));
				if (!K.IsNearlyZero())
				{
					V = K;
				}
			}
		}
		return V;
	}

	static bool Presionado(const UObject* Ctx, const TCHAR* Ruta, const TCHAR* TeclaRespaldo)
	{
		bool b = false;
		if (UEnhancedPlayerInput* EPI = PlayerInput(Ctx))
		{
			if (const UInputAction* A = Accion(Ruta))
			{
				b = EPI->GetActionValue(A).Get<bool>();
			}
		}
		if (!b)
		{
			if (APlayerController* P = PC(Ctx))
			{
				b = P->IsInputKeyDown(FKey(TeclaRespaldo));
			}
		}
		return b;
	}

	/** Flanco de subida por fotograma: estable aunque se consulte varias veces en el mismo fotograma. */
	struct FFlanco
	{
		uint64 UltFrame = MAX_uint64;
		bool Prev = false;
		bool Cur = false;
	};

	static bool Flanco(FFlanco& F, const UObject* Ctx, const TCHAR* Ruta, const TCHAR* Tecla)
	{
		if (F.UltFrame != GFrameCounter)
		{
			F.UltFrame = GFrameCounter;
			F.Prev = F.Cur;
			F.Cur = Presionado(Ctx, Ruta, Tecla);
		}
		return F.Cur && !F.Prev;
	}
}

float UJWEntradaVR::MoverX(const UObject* WorldContextObject)
{
	return static_cast<float>(JWEntradaVRPrivate::Mover(WorldContextObject).X);
}

float UJWEntradaVR::MoverY(const UObject* WorldContextObject)
{
	return static_cast<float>(JWEntradaVRPrivate::Mover(WorldContextObject).Y);
}

bool UJWEntradaVR::BotonAPulsado(const UObject* WorldContextObject)
{
	static JWEntradaVRPrivate::FFlanco F;
	return JWEntradaVRPrivate::Flanco(F, WorldContextObject, JWEntradaVRPrivate::RutaBotonA, TEXT("OculusTouch_Right_A_Click"));
}

bool UJWEntradaVR::GatilloPulsado(const UObject* WorldContextObject)
{
	static JWEntradaVRPrivate::FFlanco F;
	return JWEntradaVRPrivate::Flanco(F, WorldContextObject, JWEntradaVRPrivate::RutaGatillo, TEXT("OculusTouch_Right_Trigger_Click"));
}

static UEnhancedInputLocalPlayerSubsystem* JWSubsistemaPrueba(const UObject* Ctx)
{
	APlayerController* P = JWEntradaVRPrivate::PC(Ctx);
	if (!P || !P->GetLocalPlayer())
	{
		return nullptr;
	}
	UEnhancedInputLocalPlayerSubsystem* S = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(P->GetLocalPlayer());
	if (S)
	{
		if (const UInputMappingContext* IMC = LoadObject<UInputMappingContext>(nullptr, TEXT("/Game/XRFramework/Input/IMC_Default.IMC_Default")))
		{
			if (!S->HasMappingContext(IMC))
			{
				S->AddMappingContext(IMC, 0);
			}
		}
	}
	return S;
}

bool UJWEntradaVR::PruebaInyectar(const UObject* WorldContextObject, const FString& NombreAccion, FVector Valor)
{
	UEnhancedInputLocalPlayerSubsystem* S = JWSubsistemaPrueba(WorldContextObject);
	const UInputAction* A = LoadObject<UInputAction>(nullptr, *FString::Printf(TEXT("/Game/JWN/Input/IA_JW_%s.IA_JW_%s"), *NombreAccion, *NombreAccion));
	if (!S || !A)
	{
		return false;
	}
	S->InjectInputVectorForAction(A, Valor, {}, {});
	return true;
}

bool UJWEntradaVR::PruebaInyectarContinuo(const UObject* WorldContextObject, const FString& NombreAccion, FVector Valor, bool bIniciar)
{
	UEnhancedInputLocalPlayerSubsystem* S = JWSubsistemaPrueba(WorldContextObject);
	UInputAction* A = LoadObject<UInputAction>(nullptr, *FString::Printf(TEXT("/Game/JWN/Input/IA_JW_%s.IA_JW_%s"), *NombreAccion, *NombreAccion));
	if (!S || !A)
	{
		return false;
	}
	if (bIniciar)
	{
		S->StartContinuousInputInjectionForAction(A, FInputActionValue(A->ValueType, Valor), {}, {});
	}
	else
	{
		S->StopContinuousInputInjectionForAction(A);
	}
	return true;
}

FString UJWEntradaVR::Diagnostico(const UObject* WorldContextObject)
{
	const FVector2D M = JWEntradaVRPrivate::Mover(WorldContextObject);
	const bool bPI = JWEntradaVRPrivate::PlayerInput(WorldContextObject) != nullptr;
	return FString::Printf(TEXT("mover=%.2f,%.2f A=%d gatillo=%d enhanced=%d accMover=%d"),
		M.X, M.Y,
		JWEntradaVRPrivate::Presionado(WorldContextObject, JWEntradaVRPrivate::RutaBotonA, TEXT("OculusTouch_Right_A_Click")) ? 1 : 0,
		JWEntradaVRPrivate::Presionado(WorldContextObject, JWEntradaVRPrivate::RutaGatillo, TEXT("OculusTouch_Right_Trigger_Click")) ? 1 : 0,
		bPI ? 1 : 0,
		JWEntradaVRPrivate::Accion(JWEntradaVRPrivate::RutaMover) ? 1 : 0);
}
