// Jatun Wasi - modulo runtime de la guia Adela (sin dependencia de Convai: se consulta por reflexion).
using UnrealBuildTool;

public class JWGuia : ModuleRules
{
	public JWGuia(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine" });
	}
}
