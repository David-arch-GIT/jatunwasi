// Jatun Wasi Nawpa Kay - tesis VR Quest 2
// UJWGuiaComponent: Adela como guia que ACOMPANA al visitante.
//  - Camina DELANTE por rutas horneadas (polilineas validadas sobre el NavMesh, cruzando las barreras).
//  - Si el visitante se queda atras se detiene, lo mira y avisa UNA vez por tramo ("No te quedes atras").
//  - En cada lugar (estacion) espera mirandolo y pregunta "¿Tienes alguna pregunta?..." (Convai con el grip).
//  - Cuando el visitante vuelve hacia ella (o ya toma el camino siguiente) anuncia el siguiente tramo y guia.
//  - Al subir al 2do piso de la Hacienda pasa al salon de baile (final del recorrido).
//  - VOCES SIN CHOQUES: sus frases usan SC_Narracion con prioridad menor; si hay una narracion/cartela sonando
//    la frase es rechazada y se REINTENTA despues; nunca habla mientras Convai habla o el microfono esta abierto.
//  - Mientras Convai habla o escucha, Adela se detiene y mira al visitante.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "JWGuiaComponent.generated.h"

class USoundBase;
class UAnimSequence;
class UAudioComponent;
class USkeletalMeshComponent;

USTRUCT(BlueprintType)
struct FJWGuiaTramo
{
	GENERATED_BODY()

	/** Ruta horneada: Puntos[0] = estacion anterior, ultimo = estacion de este lugar. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TArray<FVector> Puntos;

	/** Frase al empezar el tramo ("Sigueme..."). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<USoundBase> FraseInicio = nullptr;

	/** Frase al llegar el visitante a la estacion ("¿Tienes alguna pregunta?..."). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<USoundBase> FrasePreguntas = nullptr;
};

UENUM(BlueprintType)
enum class EJWGuiaEstado : uint8
{
	Inicio,
	Guiando,
	Esperando,
	EnEstacion,
	Final
};

UCLASS(ClassGroup = (JatunWasi), meta = (BlueprintSpawnableComponent))
class JWGUIA_API UJWGuiaComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UJWGuiaComponent();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ---------------- Configuracion ----------------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TArray<FJWGuiaTramo> Tramos;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<USoundBase> FraseNoTeQuedes = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<UAnimSequence> AnimIdle = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<UAnimSequence> AnimWalk = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<UAnimSequence> AnimTalk = nullptr;

	/** Actor con el audio de la intro (Adela_Intro_Audio). Adela no arranca hasta que termine. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	TObjectPtr<AActor> AudioIntro = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float EsperaInicial = 3.f;

	/** Velocidad normal (cm/s) y maxima para alcanzar/adelantarse (el visitante anda a 200 cm/s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float VelBase = 150.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float VelMax = 300.f;

	/** Velocidad natural de la animacion de caminar (cm/s) para ajustar su ritmo. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float VelNaturalAnim = 112.7f;

	/** Ventaja comoda delante del visitante (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float DistGuia = 600.f;

	/** Si el visitante queda mas atras que esto, Adela se detiene a esperarlo. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float DistEspera = 1100.f;

	/** Distancia a la que retoma la marcha cuando el visitante se acerca. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float DistReanudar = 650.f;

	/** Segundos esperando antes de decir "No te quedes atras" (una vez por tramo). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float EsperaAntesAviso = 4.f;

	/** Distancia del visitante a la estacion para hacer la pregunta. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float DistPregunta = 900.f;

	/** Correccion de yaw si el frente de la malla no es +X del actor. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float YawOffsetMalla = 0.f;

	/** Final: al subir el visitante al 2do piso de la Hacienda, Adela pasa al salon de baile. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	FVector SalonPos = FVector(-8520.f, -1560.f, 438.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float SalonYaw = -27.5f;

	/** Altura de camara (z) que indica que el visitante ya subio al 2do piso. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float AlturaFinalZ = 380.f;

	/** Solo cuenta como 2do piso de la Hacienda si x de la camara < este valor. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guia")
	float FinalMaxX = -6500.f;

	// ---------------- Estado (lectura) ----------------
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guia|Estado")
	EJWGuiaEstado Estado = EJWGuiaEstado::Inicio;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guia|Estado")
	int32 TramoActual = -1;

	/** Texto con el estado interno (para pruebas). */
	UFUNCTION(BlueprintCallable, Category = "Guia")
	FString DebugEstado() const;

	/** Pruebas: coloca a Adela en la estacion del tramo I (EnEstacion). */
	UFUNCTION(BlueprintCallable, Category = "Guia")
	void ForzarEstacion(int32 I);

private:
	float Ahora() const;
	FVector PosVisitante() const;
	bool ConvaiOcupado();
	bool IntroSonando() const;

	// Voz con reintento (nunca pisa una narracion)
	void Decir(USoundBase* S);
	void TickVoz(bool bOcupado);
	bool AdelaHablando() const;

	void PonerAnim(UAnimSequence* A, float Rate);
	void Mirar(const FVector& Objetivo, float Dt);
	void MirarDireccion(const FVector& Dir, float Dt);
	void ColocarEnRuta(float S, float Dt, FVector& OutDir);
	float SueloZ(const FVector& P) const;

	float LargoTramo(int32 I) const;
	float ProyectarEnTramo(int32 I, const FVector& P, float& OutLateral) const;
	FVector PuntoEnTramo(int32 I, float S, FVector& OutDir) const;

	void IniciarTramo(int32 I);
	void IrAlFinal();
	/** Reinicio: si los creditos del pawn (componente "CreditosFinal") llevan >= 4 s visibles, A o gatillo recargan el mapa. */
	void ComprobarReinicio(float Dt);

	UPROPERTY(Transient)
	TObjectPtr<USceneComponent> CreditosVis = nullptr;
	float TCreditos = 0.f;
	bool bReiniciando = false;

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> Malla = nullptr;

	UPROPERTY(Transient)
	TObjectPtr<UActorComponent> Chatbot = nullptr;

	UPROPERTY(Transient)
	TObjectPtr<UActorComponent> ConvaiJugador = nullptr;

	UPROPERTY(Transient)
	TObjectPtr<UAudioComponent> Voz = nullptr;

	UPROPERTY(Transient)
	TObjectPtr<UAudioComponent> VozIntro = nullptr;

	UPROPERTY(Transient)
	TObjectPtr<USoundBase> Pendiente = nullptr;

	TArray<TArray<float>> Acum;
	float T0 = 0.f;
	float SAdela = 0.f;
	float TInicioTramo = 0.f;
	float TEspera = 0.f;
	float TCercaEstacion = 0.f;
	bool bAvisoHecho = false;
	bool bPreguntaHecha = false;
	bool bLlegoVisitante = false;
	bool bSeAlejo = false;
	bool bMoviendose = false;
	float VelActual = 0.f;
	float VelVisitante = 0.f;
	FVector PrevVisitante = FVector::ZeroVector;
	bool bPrevValido = false;
	float ZSuave = 0.f;
	bool bZValido = false;

	// voz
	float PendDesde = 0.f;
	float UltIntento = -100.f;
	float InicioLinea = 0.f;
	int32 Interrupciones = 0;
	bool bLineaSonando = false;
	int32 LineasDichas = 0;
	int32 LineasRechazadas = 0;

	bool bBuscoConvaiJugador = false;
	bool bOcupadoUlt = false;
	float TBusquedaConvai = -100.f;
	float TDiag = 0.f;

	/** true si otra voz grabada (clase SCL_Voz) esta sonando en este mundo (para no intentar hablar encima). */
	bool OtraVozSonando() const;
};
