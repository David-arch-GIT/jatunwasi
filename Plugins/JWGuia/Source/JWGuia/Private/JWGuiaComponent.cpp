// Jatun Wasi Nawpa Kay - tesis VR Quest 2
// Adela guia que acompana. Ver descripcion en JWGuiaComponent.h
#include "JWGuiaComponent.h"

#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/AudioComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundClass.h"
#include "GameFramework/PlayerController.h"
#include "NavigationSystem.h"
#include "InputCoreTypes.h"
#include "JWEntradaVR.h"
#include "UObject/UObjectIterator.h"

UJWGuiaComponent::UJWGuiaComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
}

float UJWGuiaComponent::Ahora() const
{
	const UWorld* W = GetWorld();
	return W ? W->GetTimeSeconds() : 0.f;
}

void UJWGuiaComponent::BeginPlay()
{
	Super::BeginPlay();
	AActor* Owner = GetOwner();
	if (!Owner)
	{
		return;
	}
	Malla = Owner->FindComponentByClass<USkeletalMeshComponent>();
	for (UActorComponent* C : Owner->GetComponents())
	{
		if (C && C->GetClass()->GetName().Contains(TEXT("ConvaiChatbot")))
		{
			Chatbot = C;
			break;
		}
	}
	Voz = NewObject<UAudioComponent>(Owner, TEXT("VozGuiaJW"));
	if (Voz)
	{
		Voz->bAutoActivate = false;
		Voz->bAllowSpatialization = false; // como las narraciones: suena "en los oidos"
		Voz->bIsUISound = false;
		if (Owner->GetRootComponent())
		{
			Voz->SetupAttachment(Owner->GetRootComponent());
		}
		Voz->RegisterComponent();
	}
	VozIntro = AudioIntro ? AudioIntro->FindComponentByClass<UAudioComponent>() : nullptr;

	Acum.SetNum(Tramos.Num());
	for (int32 I = 0; I < Tramos.Num(); ++I)
	{
		const TArray<FVector>& P = Tramos[I].Puntos;
		Acum[I].SetNum(P.Num());
		float S = 0.f;
		for (int32 K = 0; K < P.Num(); ++K)
		{
			if (K > 0)
			{
				S += FVector::Dist2D(P[K - 1], P[K]);
			}
			Acum[I][K] = S;
		}
	}
	T0 = Ahora();
	Estado = EJWGuiaEstado::Inicio;
	TramoActual = -1;
}

FVector UJWGuiaComponent::PosVisitante() const
{
	if (APlayerCameraManager* PCM = UGameplayStatics::GetPlayerCameraManager(this, 0))
	{
		return PCM->GetCameraLocation();
	}
	if (APawn* P = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		return P->GetActorLocation();
	}
	return FVector::ZeroVector;
}

bool UJWGuiaComponent::ConvaiOcupado()
{
	// 1) Adela (Convai) hablando
	if (Chatbot)
	{
		if (UFunction* F = Chatbot->FindFunction(TEXT("GetIsTalking")))
		{
			if (F->ParmsSize > 0)
			{
				uint8* Buf = static_cast<uint8*>(FMemory_Alloca(F->ParmsSize));
				FMemory::Memzero(Buf, F->ParmsSize);
				Chatbot->ProcessEvent(F, Buf);
				if (const FBoolProperty* R = CastField<FBoolProperty>(F->GetReturnProperty()))
				{
					if (R->GetPropertyValue_InContainer(Buf))
					{
						return true;
					}
				}
			}
		}
	}
	// 2) Microfono abierto (el visitante mantiene el grip): ConvaiPlayer.bMute == false
	//    Se re-busca cada segundo (o si la referencia quedo invalida / de otro pawn): robusto ante
	//    reinstanciado de componentes y cambio de pawn.
	APawn* PawnAct = UGameplayStatics::GetPlayerPawn(this, 0);
	const float TNow = Ahora();
	if (PawnAct && (!ConvaiJugador || !IsValid(ConvaiJugador) || ConvaiJugador->GetOwner() != PawnAct || (TNow - TBusquedaConvai) > 1.f))
	{
		TBusquedaConvai = TNow;
		ConvaiJugador = nullptr;
		for (UActorComponent* C : PawnAct->GetComponents())
		{
			if (C && IsValid(C) && C->GetClass()->GetName().Contains(TEXT("ConvaiPlayer")))
			{
				ConvaiJugador = C;
				break;
			}
		}
	}
	if (ConvaiJugador && IsValid(ConvaiJugador))
	{
		if (const FBoolProperty* M = FindFProperty<FBoolProperty>(ConvaiJugador->GetClass(), TEXT("bMute")))
		{
			if (!M->GetPropertyValue_InContainer(ConvaiJugador.Get()))
			{
				return true;
			}
		}
	}
	return false;
}

bool UJWGuiaComponent::IntroSonando() const
{
	return VozIntro && VozIntro->IsPlaying();
}

// ---------------------------------------------------------------- voz
void UJWGuiaComponent::Decir(USoundBase* S)
{
	if (!S || Pendiente == S)
	{
		return;
	}
	if (bLineaSonando && Voz)
	{
		Voz->Stop();
	}
	Pendiente = S;
	PendDesde = Ahora();
	Interrupciones = 0;
	bLineaSonando = false;
	UltIntento = -100.f;
}

void UJWGuiaComponent::TickVoz(bool bOcupado)
{
	if (!Pendiente || !Voz)
	{
		return;
	}
	const float T = Ahora();
	const float Dur = FMath::Max(Pendiente->GetDuration(), 0.5f);
	if (bLineaSonando)
	{
		const bool bSigue = Voz->IsPlaying() && (T - InicioLinea) < Dur + 3.f;
		if (bSigue)
		{
			return;
		}
		if (Voz->IsPlaying())
		{
			Voz->Stop();
		}
		bLineaSonando = false;
		const float Jugado = T - InicioLinea;
		if (Jugado >= Dur * 0.85f)
		{
			Pendiente = nullptr; // dicha completa
			++LineasDichas;
			return;
		}
		if (Jugado > 0.8f)
		{
			++Interrupciones; // la corto una narracion/cartela: se repite luego
		}
		else
		{
			++LineasRechazadas; // habia una narracion sonando: se reintenta
		}
		if (Interrupciones > 2)
		{
			Pendiente = nullptr;
			return;
		}
		UltIntento = T;
		return;
	}
	if (T - PendDesde > 150.f)
	{
		Pendiente = nullptr; // se rinde (no insiste para siempre)
		return;
	}
	if (bOcupado || (T - UltIntento) < 1.5f)
	{
		return;
	}
	if (OtraVozSonando())
	{
		UltIntento = T; // hay una narracion/cartela sonando: espera su turno (no habla encima)
		return;
	}
	Voz->SetSound(Pendiente);
	Voz->Play();
	InicioLinea = T;
	UltIntento = T;
	bLineaSonando = true;
}

bool UJWGuiaComponent::OtraVozSonando() const
{
	const UWorld* W = GetWorld();
	const USoundClass* ClaseVoz = Pendiente ? Pendiente->GetSoundClass() : nullptr;
	if (!W || !ClaseVoz)
	{
		return false;
	}
	for (TObjectIterator<UAudioComponent> It; It; ++It)
	{
		const UAudioComponent* C = *It;
		if (!C || C == Voz || C->GetWorld() != W || !C->IsPlaying())
		{
			continue;
		}
		const USoundBase* S = C->Sound;
		if (S && S->GetSoundClass() == ClaseVoz)
		{
			return true;
		}
	}
	return false;
}

bool UJWGuiaComponent::AdelaHablando() const
{
	return bLineaSonando && Voz && Voz->IsPlaying();
}

// ---------------------------------------------------------------- animacion / orientacion
void UJWGuiaComponent::PonerAnim(UAnimSequence* A, float Rate)
{
	if (!Malla || !A)
	{
		return;
	}
	UAnimSingleNodeInstance* SI = Malla->GetSingleNodeInstance();
	if (!SI || SI->GetAnimationAsset() != A)
	{
		Malla->PlayAnimation(A, true);
	}
	Malla->SetPlayRate(Rate);
}

void UJWGuiaComponent::MirarDireccion(const FVector& Dir, float Dt)
{
	AActor* Owner = GetOwner();
	FVector D = Dir;
	D.Z = 0.f;
	if (!Owner || D.SizeSquared() < 1.f)
	{
		return;
	}
	const FRotator Cur(0.f, Owner->GetActorRotation().Yaw, 0.f);
	const FRotator Tgt(0.f, D.Rotation().Yaw + YawOffsetMalla, 0.f);
	Owner->SetActorRotation(FMath::RInterpTo(Cur, Tgt, Dt, 4.f));
}

void UJWGuiaComponent::Mirar(const FVector& Objetivo, float Dt)
{
	if (AActor* Owner = GetOwner())
	{
		MirarDireccion(Objetivo - Owner->GetActorLocation(), Dt);
	}
}

// ---------------------------------------------------------------- rutas
float UJWGuiaComponent::LargoTramo(int32 I) const
{
	return (Acum.IsValidIndex(I) && Acum[I].Num() > 0) ? Acum[I].Last() : 0.f;
}

FVector UJWGuiaComponent::PuntoEnTramo(int32 I, float S, FVector& OutDir) const
{
	OutDir = FVector::ZeroVector;
	if (!Tramos.IsValidIndex(I) || Tramos[I].Puntos.Num() == 0)
	{
		return GetOwner() ? GetOwner()->GetActorLocation() : FVector::ZeroVector;
	}
	const TArray<FVector>& P = Tramos[I].Puntos;
	const TArray<float>& Ac = Acum[I];
	if (P.Num() == 1 || S <= 0.f)
	{
		if (P.Num() > 1)
		{
			OutDir = P[1] - P[0];
		}
		return P[0];
	}
	for (int32 K = 1; K < P.Num(); ++K)
	{
		if (S <= Ac[K] || K == P.Num() - 1)
		{
			const float Seg = FMath::Max(Ac[K] - Ac[K - 1], 1.f);
			const float A = FMath::Clamp((S - Ac[K - 1]) / Seg, 0.f, 1.f);
			OutDir = P[K] - P[K - 1];
			return FMath::Lerp(P[K - 1], P[K], A);
		}
	}
	return P.Last();
}

float UJWGuiaComponent::ProyectarEnTramo(int32 I, const FVector& Q, float& OutLateral) const
{
	OutLateral = UE_BIG_NUMBER;
	if (!Tramos.IsValidIndex(I) || Tramos[I].Puntos.Num() < 2)
	{
		return 0.f;
	}
	const TArray<FVector>& P = Tramos[I].Puntos;
	const TArray<float>& Ac = Acum[I];
	float MejorS = 0.f;
	const FVector2D Q2(Q.X, Q.Y);
	for (int32 K = 1; K < P.Num(); ++K)
	{
		const FVector2D A(P[K - 1].X, P[K - 1].Y);
		const FVector2D B(P[K].X, P[K].Y);
		const FVector2D AB = B - A;
		const float L2 = FMath::Max(AB.SizeSquared(), 1.f);
		const float T = FMath::Clamp(FVector2D::DotProduct(Q2 - A, AB) / L2, 0.f, 1.f);
		const FVector2D C = A + AB * T;
		const float D = FVector2D::Distance(Q2, C);
		if (D < OutLateral)
		{
			OutLateral = D;
			MejorS = Ac[K - 1] + (Ac[K] - Ac[K - 1]) * T;
		}
	}
	return MejorS;
}

float UJWGuiaComponent::SueloZ(const FVector& P) const
{
	const UWorld* W = GetWorld();
	if (!W)
	{
		return P.Z;
	}
	FCollisionQueryParams Q(SCENE_QUERY_STAT(JWGuiaSuelo), false, GetOwner());
	if (APawn* Pw = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		Q.AddIgnoredActor(Pw);
	}
	FHitResult H;
	if (W->LineTraceSingleByChannel(H, P + FVector(0, 0, 120.f), P - FVector(0, 0, 250.f), ECC_Visibility, Q))
	{
		if (FMath::Abs(H.ImpactPoint.Z - P.Z) < 90.f)
		{
			return H.ImpactPoint.Z;
		}
	}
	return P.Z;
}

void UJWGuiaComponent::ColocarEnRuta(float S, float Dt, FVector& OutDir)
{
	AActor* Owner = GetOwner();
	if (!Owner)
	{
		return;
	}
	const FVector P = PuntoEnTramo(TramoActual, S, OutDir);
	const float Z = SueloZ(P);
	ZSuave = bZValido ? FMath::FInterpTo(ZSuave, Z, Dt, 10.f) : Z;
	bZValido = true;
	Owner->SetActorLocation(FVector(P.X, P.Y, ZSuave), false, nullptr, ETeleportType::TeleportPhysics);
}

// ---------------------------------------------------------------- estados
void UJWGuiaComponent::IniciarTramo(int32 I)
{
	if (!Tramos.IsValidIndex(I))
	{
		return;
	}
	TramoActual = I;
	SAdela = 0.f;
	VelActual = 0.f;
	bAvisoHecho = false;
	TInicioTramo = Ahora();
	Estado = EJWGuiaEstado::Guiando;
	bZValido = false;
	Decir(Tramos[I].FraseInicio);
}

void UJWGuiaComponent::ComprobarReinicio(float Dt)
{
	// La lectura de A y del gatillo usa un flanco estable por fotograma: llamarla aqui no le quita la pulsacion al pawn.
	const bool bA = UJWEntradaVR::BotonAPulsado(this);
	const bool bG = UJWEntradaVR::GatilloPulsado(this);
	if (bReiniciando)
	{
		return;
	}
	if (!CreditosVis)
	{
		APawn* P = UGameplayStatics::GetPlayerPawn(this, 0);
		if (!P)
		{
			return;
		}
		TArray<USceneComponent*> Comps;
		P->GetComponents<USceneComponent>(Comps);
		for (USceneComponent* C : Comps)
		{
			if (C && C->GetName().StartsWith(TEXT("CreditosFinal")))
			{
				CreditosVis = C;
				break;
			}
		}
		if (!CreditosVis)
		{
			return;
		}
	}
	if (!CreditosVis->IsVisible())
	{
		TCreditos = 0.f;
		return;
	}
	TCreditos += Dt;
	if (TCreditos >= 4.f && (bA || bG))
	{
		bReiniciando = true;
		UE_LOG(LogTemp, Log, TEXT("JWGuia: reinicio del recorrido solicitado tras los creditos"));
		UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
	}
}

void UJWGuiaComponent::IrAlFinal()
{
	if (AActor* Owner = GetOwner())
	{
		Owner->SetActorLocationAndRotation(SalonPos, FRotator(0.f, SalonYaw, 0.f), false, nullptr, ETeleportType::TeleportPhysics);
	}
	Estado = EJWGuiaEstado::Final;
	bMoviendose = false;
	VelActual = 0.f;
	Pendiente = nullptr; // no queda ninguna frase de guia pendiente para el final
	if (Voz && bLineaSonando)
	{
		Voz->Stop();
	}
	bLineaSonando = false;
}

void UJWGuiaComponent::ForzarEstacion(int32 I)
{
	if (!Tramos.IsValidIndex(I) || Tramos[I].Puntos.Num() == 0)
	{
		return;
	}
	TramoActual = I;
	SAdela = LargoTramo(I);
	FVector Dir;
	bZValido = false;
	ColocarEnRuta(SAdela, 0.f, Dir);
	Estado = EJWGuiaEstado::EnEstacion;
	bPreguntaHecha = false;
	bLlegoVisitante = false;
	bSeAlejo = false;
	TCercaEstacion = 0.f;
}

void UJWGuiaComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Owner = GetOwner();
	if (!Owner || !GetWorld() || DeltaTime <= 0.f)
	{
		return;
	}
	const float Dt = FMath::Min(DeltaTime, 0.1f);
	const float T = Ahora();
	const FVector U = PosVisitante();
	if (bPrevValido)
	{
		const float Inst = FVector::Dist2D(U, PrevVisitante) / Dt;
		VelVisitante = FMath::FInterpTo(VelVisitante, FMath::Min(Inst, 600.f), Dt, 3.f);
	}
	PrevVisitante = U;
	bPrevValido = true;

	// Reinicio del recorrido (pedido de la usuaria 2026-11-24): con los creditos finales visibles al menos
	// 4 s, el boton A o el gatillo derecho recargan el mapa desde el inicio.
	ComprobarReinicio(Dt);

#if !UE_BUILD_SHIPPING
	// DIAGNOSTICO temporal (solo builds Development, no existe en Shipping): estado de la entrada y del NavMesh
	TDiag += Dt;
	if (TDiag > 2.f)
	{
		TDiag = 0.f;
		APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
		APawn* PW = UGameplayStatics::GetPlayerPawn(this, 0);
		const float RX = PC ? PC->GetInputAnalogKeyState(FKey(TEXT("OculusTouch_Right_Thumbstick_X"))) : -9.f;
		const float RY = PC ? PC->GetInputAnalogKeyState(FKey(TEXT("OculusTouch_Right_Thumbstick_Y"))) : -9.f;
		const float LX = PC ? PC->GetInputAnalogKeyState(FKey(TEXT("OculusTouch_Left_Thumbstick_X"))) : -9.f;
		const float LY = PC ? PC->GetInputAnalogKeyState(FKey(TEXT("OculusTouch_Left_Thumbstick_Y"))) : -9.f;
		const bool TR = PC ? PC->IsInputKeyDown(FKey(TEXT("OculusTouch_Right_Trigger_Click"))) : false;
		const bool BA = PC ? PC->IsInputKeyDown(FKey(TEXT("OculusTouch_Right_A_Click"))) : false;
		const FVector PL = PW ? PW->GetActorLocation() : FVector::ZeroVector;
		bool bNav = false;
		bool bNavSys = false;
		if (UNavigationSystemV1* NS = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()))
		{
			bNavSys = true;
			FNavLocation NL;
			bNav = NS->ProjectPointToNavigation(PL, NL, FVector(300.f, 300.f, 400.f));
		}
		UE_LOG(LogTemp, Warning, TEXT("JWDIAG teclas rx=%.2f ry=%.2f lx=%.2f ly=%.2f trig=%d a=%d | acciones %s | pawn=%.0f,%.0f,%.0f navsys=%d nav=%d pc=%d %s"),
			RX, RY, LX, LY, TR ? 1 : 0, BA ? 1 : 0, *UJWEntradaVR::Diagnostico(this), PL.X, PL.Y, PL.Z, bNavSys ? 1 : 0, bNav ? 1 : 0, PC ? 1 : 0, *DebugEstado());
	}
#endif

	const bool bOcupado = ConvaiOcupado();
	bOcupadoUlt = bOcupado;
	TickVoz(bOcupado);
	const float DUser = FVector::Dist2D(Owner->GetActorLocation(), U);
	bMoviendose = false;

	// Final del recorrido: el visitante subio al 2do piso de la Hacienda
	if (Estado != EJWGuiaEstado::Final && U.Z > AlturaFinalZ && U.X < FinalMaxX)
	{
		IrAlFinal();
	}

	switch (Estado)
	{
	case EJWGuiaEstado::Inicio:
	{
		Mirar(U, Dt);
		if (T - T0 > EsperaInicial && !IntroSonando() && !bOcupado && Tramos.Num() > 0)
		{
			IniciarTramo(0);
		}
		break;
	}
	case EJWGuiaEstado::Guiando:
	{
		if (bOcupado || (T - TInicioTramo) < 1.5f)
		{
			Mirar(U, Dt); // se detiene a conversar / dice "Sigueme" mirandolo
			VelActual = 0.f;
			break;
		}
		float Lat = 0.f;
		const float SU = ProyectarEnTramo(TramoActual, U, Lat);
		const float Gap = SAdela - SU;
		const float L = LargoTramo(TramoActual);
		if (Gap > DistEspera || (Lat > 1500.f && DUser > DistEspera))
		{
			Estado = EJWGuiaEstado::Esperando;
			TEspera = T;
			VelActual = 0.f;
			Mirar(U, Dt);
			break;
		}
		float V;
		if (Gap < 0.f)
		{
			V = VelMax; // el visitante se adelanto: lo alcanza
		}
		else if (Gap < 300.f)
		{
			V = FMath::Clamp(VelVisitante + 60.f, VelBase, VelMax); // lo lleva de cerca, sin dejarse alcanzar
		}
		else if (Gap < DistGuia)
		{
			V = VelBase;
		}
		else
		{
			V = VelBase * 0.6f; // va lejos adelante: baja el ritmo
		}
		VelActual = FMath::FInterpTo(VelActual, V, Dt, 2.5f);
		SAdela = FMath::Min(SAdela + VelActual * Dt, L);
		FVector Dir;
		ColocarEnRuta(SAdela, Dt, Dir);
		MirarDireccion(Dir, Dt);
		bMoviendose = VelActual > 5.f;
		if (SAdela >= L - 1.f)
		{
			Estado = EJWGuiaEstado::EnEstacion;
			bPreguntaHecha = false;
			bLlegoVisitante = false;
			bSeAlejo = false;
			TCercaEstacion = 0.f;
			VelActual = 0.f;
			bMoviendose = false;
		}
		break;
	}
	case EJWGuiaEstado::Esperando:
	{
		Mirar(U, Dt);
		VelActual = 0.f;
		float Lat = 0.f;
		const float SU = ProyectarEnTramo(TramoActual, U, Lat);
		const float Gap = SAdela - SU;
		if (!bOcupado && !bAvisoHecho && (T - TEspera) > EsperaAntesAviso)
		{
			Decir(FraseNoTeQuedes); // una sola vez por tramo
			bAvisoHecho = true;
		}
		if (DUser < DistReanudar || (Gap < 0.f && Lat < 800.f))
		{
			Estado = EJWGuiaEstado::Guiando;
		}
		break;
	}
	case EJWGuiaEstado::EnEstacion:
	{
		Mirar(U, Dt);
		if (DUser < DistPregunta)
		{
			bLlegoVisitante = true;
		}
		if (bLlegoVisitante && !bPreguntaHecha && !bOcupado && Tramos.IsValidIndex(TramoActual))
		{
			Decir(Tramos[TramoActual].FrasePreguntas);
			bPreguntaHecha = true;
		}
		const bool bPreguntaTerminada = bPreguntaHecha && Pendiente == nullptr;
		if (bPreguntaHecha && DUser > 1000.f)
		{
			bSeAlejo = true;
		}
		TCercaEstacion = (DUser < 600.f) ? TCercaEstacion + Dt : 0.f;
		const int32 Sig = TramoActual + 1;
		if (Tramos.IsValidIndex(Sig) && bPreguntaTerminada && !bOcupado)
		{
			float LatN = 0.f;
			const float SN = ProyectarEnTramo(Sig, U, LatN);
			const bool bVuelve = bSeAlejo && DUser < 600.f;                     // volvio donde Adela
			const bool bYaVa = SN > 1500.f && LatN < 800.f && DUser > 1200.f;    // ya tomo el camino siguiente
			const bool bSeQuedo = TCercaEstacion > 45.f;                         // se quedo con ella
			if (bVuelve || bYaVa || bSeQuedo)
			{
				IniciarTramo(Sig);
			}
		}
		break;
	}
	case EJWGuiaEstado::Final:
	default:
	{
		if (DUser < 2000.f)
		{
			Mirar(U, Dt);
		}
		break;
	}
	}

	// Animacion (si Convai habla, la maneja el Blueprint: hablar/reposo)
	if (!bOcupado)
	{
		if (bMoviendose)
		{
			PonerAnim(AnimWalk, FMath::Clamp(VelActual / FMath::Max(VelNaturalAnim, 1.f), 0.6f, 2.7f));
		}
		else if (AdelaHablando() || (Estado == EJWGuiaEstado::Inicio && IntroSonando()))
		{
			PonerAnim(AnimTalk, 1.f);
		}
		else
		{
			PonerAnim(AnimIdle, 1.f);
		}
	}
}

FString UJWGuiaComponent::DebugEstado() const
{
	static const TCHAR* Nombres[] = { TEXT("Inicio"), TEXT("Guiando"), TEXT("Esperando"), TEXT("EnEstacion"), TEXT("Final") };
	const int32 E = FMath::Clamp(static_cast<int32>(Estado), 0, 4);
	const FVector A = GetOwner() ? GetOwner()->GetActorLocation() : FVector::ZeroVector;
	return FString::Printf(
		TEXT("estado=%s tramo=%d s=%.0f/%.0f vel=%.0f velVis=%.0f pos=%.0f,%.0f,%.0f yaw=%.1f pend=%s sonando=%d dichas=%d rech=%d preg=%d llego=%d alejo=%d aviso=%d mov=%d ocup=%d cj=%s cb=%s"),
		Nombres[E], TramoActual, SAdela, LargoTramo(TramoActual), VelActual, VelVisitante, A.X, A.Y, A.Z,
		GetOwner() ? GetOwner()->GetActorRotation().Yaw : 0.f,
		Pendiente ? *Pendiente->GetName() : TEXT("-"), bLineaSonando ? 1 : 0, LineasDichas, LineasRechazadas,
		bPreguntaHecha ? 1 : 0, bLlegoVisitante ? 1 : 0, bSeAlejo ? 1 : 0, bAvisoHecho ? 1 : 0, bMoviendose ? 1 : 0,
		bOcupadoUlt ? 1 : 0, ConvaiJugador ? *ConvaiJugador->GetName() : TEXT("-"), Chatbot ? *Chatbot->GetName() : TEXT("-"));
}
