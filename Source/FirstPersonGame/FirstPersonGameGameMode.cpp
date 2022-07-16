// Copyright Epic Games, Inc. All Rights Reserved.

#include "FirstPersonGameGameMode.h"
#include "FirstPersonGameCharacter.h"
#include "UObject/ConstructorHelpers.h"

AFirstPersonGameGameMode::AFirstPersonGameGameMode()
	: Super()
{
	// set default pawn class to our Blueprinted character
	static ConstructorHelpers::FClassFinder<APawn> PlayerPawnClassFinder(TEXT("/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"));
	DefaultPawnClass = PlayerPawnClassFinder.Class;

}
