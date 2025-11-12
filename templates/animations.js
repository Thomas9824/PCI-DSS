// Module auto-exécuté pour éviter la pollution de l'espace de noms global
(function () {
  
  // Fonction utilitaire pour créer une couleur RGBA blanche avec opacité variable
  // Prend une valeur d'opacité et la clamp entre 0 et 1 pour éviter les erreurs
  const MONOCHROME_FILL = (opacity) =>
    `rgba(255, 255, 255, ${Math.max(0, Math.min(1, opacity))})`;

  // Multiplicateur global pour contrôler la vitesse de toutes les animations
  // Valeur de 0.5 = animations à demi-vitesse par rapport à la normale
  const GLOBAL_SPEED = 0.5;

  // Fonction d'easing cubique pour des transitions fluides
  // Accélération lente au début et à la fin, rapide au milieu
  // t = temps normalisé entre 0 et 1
  function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  // Fonction utilitaire pour créer un canvas dans un conteneur donné
  // Cette fonction n'est actuellement pas utilisée mais pourrait servir pour des animations futures
  function createCanvasInContainer(container) {
    // Vérification de sécurité : retourner null si le conteneur n'existe pas
    if (!container) return null;
    
    // Vider le conteneur de tout contenu existant
    container.innerHTML = "";
    
    // Créer un nouvel élément canvas
    const canvas = document.createElement("canvas");
    
    // Récupérer les dimensions actuelles du conteneur
    const rect = container.getBoundingClientRect();
    // S'assurer que les dimensions minimales sont de 100px pour éviter des canvas trop petits
    const canvasWidth = Math.max(100, rect.width);
    const canvasHeight = Math.max(100, rect.height);
    
    // Définir les dimensions réelles du canvas (résolution interne)
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    
    // Styles CSS pour que le canvas occupe tout l'espace du conteneur
    canvas.style.position = "absolute";  // Positionnement absolu par rapport au conteneur
    canvas.style.left = "0";             // Aligné à gauche
    canvas.style.top = "0";              // Aligné en haut
    canvas.style.width = "100%";         // Largeur CSS = 100% du conteneur
    canvas.style.height = "100%";        // Hauteur CSS = 100% du conteneur
    
    // Ajouter le canvas au conteneur
    container.appendChild(canvas);
    
    // Retourner un objet avec le contexte de dessin et les dimensions
    return {
      ctx: canvas.getContext("2d"),  // Contexte 2D pour dessiner
      width: canvasWidth,            // Largeur en pixels
      height: canvasHeight           // Hauteur en pixels
    };
  }

  // Animation "Helix Scanner" - Scanner hélicoïdal avec points en rotation 3D
  // Destinée à la carte "PCI Scraper"
  function setupHelixScanner() {
    // Sélectionner le conteneur spécifique dans la carte scraper
    const container = document.querySelector(".card-scraper .white-container");
    // Sortir si le conteneur n'existe pas (protection contre les erreurs)
    if (!container) return;
    
    // Créer un canvas avec une résolution haute pour une meilleure qualité
    // Résolution augmentée de 180x180 à 540x540 (3x plus haute)
    container.innerHTML = "";  // Vider le conteneur
    const canvas = document.createElement("canvas");
    canvas.width = 540;   // Résolution interne haute qualité
    canvas.height = 540;  // Résolution interne haute qualité
    
    // Styles CSS pour adapter le canvas au conteneur
    canvas.style.position = "absolute";  // Positionnement absolu
    canvas.style.left = "0";             // Pas de décalage horizontal
    canvas.style.top = "0";              // Pas de décalage vertical
    canvas.style.width = "100%";         // S'étendre sur toute la largeur du conteneur
    canvas.style.height = "100%";        // S'étendre sur toute la hauteur du conteneur
    container.appendChild(canvas);
    
    // Récupérer le contexte 2D pour dessiner
    const ctx = canvas.getContext("2d");
    
    // Variables de contrôle du temps pour l'animation
    let time = 0;      // Temps écoulé total en secondes
    let lastTime = 0;  // Timestamp de la dernière frame pour calculer deltaTime

    // Configuration de l'hélice (mise à l'échelle pour la haute résolution)
    const centerX = 540 / 2,  // Centre X du canvas (270px)
          centerY = 540 / 2;  // Centre Y du canvas (270px)
    
    // Paramètres de l'animation hélicoïdale (multipliés par 3 pour la résolution)
    const numDots = 100,      // Nombre total de points sur l'hélice
          radius = 105,       // Rayon de l'hélice (35 * 3 = 105px)
          height = 360,       // Hauteur totale de l'hélice (120 * 3 = 360px)
          dots = [];          // Tableau pour stocker les positions des points
    
    // Initialiser les positions de base des points sur l'hélice
    for (let i = 0; i < numDots; i++) {
      dots.push({ 
        angle: i * 0.3,  // Angle initial de chaque point (crée la spirale)
        y: (i / numDots) * height - height / 2  // Position Y répartie sur la hauteur, centrée
      });
    }

    // Fonction d'animation appelée à chaque frame
    function animate(timestamp) {
      // Initialiser lastTime à la première frame
      if (!lastTime) lastTime = timestamp;
      
      // Calculer le temps écoulé depuis la dernière frame (en millisecondes)
      const deltaTime = timestamp - lastTime;
      lastTime = timestamp;
      
      // Convertir en secondes et appliquer le multiplicateur de vitesse global
      time += deltaTime * 0.001 * GLOBAL_SPEED;

      // Effacer le canvas pour la nouvelle frame
      ctx.clearRect(0, 0, 540, 540);

      // Configuration du scanner qui se déplace de haut en bas
      const loopDuration = 8;  // Durée d'un cycle complet en secondes
      
      // Créer un mouvement oscillant fluide avec une fonction sinusoïdale
      const seamlessProgress = Math.sin((time / loopDuration) * Math.PI * 2);
      
      // Position Y actuelle du scanner (oscille entre -height/2 et +height/2)
      const scanY = seamlessProgress * (height / 2);
      
      // Paramètres du scanner (mis à l'échelle pour haute résolution)
      const scanWidth = 75,           // Largeur de la zone de scan (25 * 3 = 75px)
            trailLength = height * 0.3; // Longueur de la traînée derrière le scanner

      // Parcourir chaque point de l'hélice pour le dessiner
      dots.forEach((dot) => {
        // La rotation évolue avec le temps pour faire tourner l'hélice
        const rotation = time;
        
        // Calculer la position 3D du point sur l'hélice en rotation
        const x = radius * Math.cos(dot.angle + rotation);  // Position X (cosinus)
        const z = radius * Math.sin(dot.angle + rotation);  // Position Z (sinus, profondeur)
        
        // Projeter les coordonnées 3D sur le plan 2D du canvas
        const pX = centerX + x,    // Position finale X sur le canvas
              pY = centerY + dot.y; // Position finale Y sur le canvas
        
        // Calculer l'effet de profondeur (les points plus proches sont plus visibles)
        // z varie de -radius à +radius, scale varie de 0 à 1
        const scale = (z + radius) / (radius * 2);
        
        // Calculer l'influence du scanner sur ce point
        const distToScan = Math.abs(dot.y - scanY);  // Distance au scanner
        
        // Influence du bord avant du scanner (effet cosinus pour transition douce)
        const leadingEdgeInfluence =
          distToScan < scanWidth
            ? Math.cos((distToScan / scanWidth) * (Math.PI / 2))  // Transition cosinus de 1 à 0
            : 0;
        
        // Calculer l'influence de la traînée derrière le scanner
        let trailInfluence = 0;
        const distBehindScan = dot.y - scanY;  // Distance signée par rapport au scanner
        
        // Déterminer la direction du scanner (monte ou descend)
        const isMovingUp = Math.cos((time / loopDuration) * Math.PI * 2) > 0;
        
        // Appliquer la traînée selon la direction du scanner
        if (
          isMovingUp &&                              // Scanner monte
          distBehindScan < 0 &&                      // Point en dessous du scanner
          Math.abs(distBehindScan) < trailLength     // Dans la zone de traînée
        ) {
          // Traînée quadratique qui s'estompe avec la distance
          trailInfluence =
            Math.pow(1 - Math.abs(distBehindScan) / trailLength, 2) * 0.4;
        } else if (
          !isMovingUp &&                             // Scanner descend
          distBehindScan > 0 &&                      // Point au-dessus du scanner
          Math.abs(distBehindScan) < trailLength     // Dans la zone de traînée
        ) {
          // Même calcul pour la direction opposée
          trailInfluence =
            Math.pow(1 - Math.abs(distBehindScan) / trailLength, 2) * 0.4;
        }
        
        // Prendre la plus grande influence entre le bord avant et la traînée
        const totalInfluence = Math.max(leadingEdgeInfluence, trailInfluence);
        
        // Calculer la taille finale du point (base + influence du scanner, mise à l'échelle)
        const size = Math.max(0, (scale * 2.2 + totalInfluence * 3.5) * 3);
        
        // Calculer l'opacité finale (base + influence du scanner)
        const opacity = Math.max(0.2, scale * 0.7 + totalInfluence * 0.8);
        
        // Dessiner le point sur le canvas
        ctx.beginPath();
        ctx.arc(pX, pY, size, 0, Math.PI * 2);  // Cercle à la position calculée
        ctx.fillStyle = MONOCHROME_FILL(opacity);  // Couleur blanche avec opacité
        ctx.fill();  // Remplir le cercle
      });

      // Programmer la prochaine frame d'animation
      requestAnimationFrame(animate);
    }

    // Démarrer l'animation en appelant animate pour la première fois
    requestAnimationFrame(animate);
  }

  // Animation "3D Sphere Scan" - Sphère 3D avec scanner rotatif
  // Destinée à la carte "PCI Converter"
  function setup3DSphereScan() {
    // Sélectionner le conteneur spécifique dans la carte converter
    const container = document.querySelector(".card-converter .white-container");
    if (!container) return;  // Protection contre les erreurs
    
    // Créer un canvas avec une résolution haute pour une meilleure qualité
    container.innerHTML = "";
    const canvas = document.createElement("canvas");
    canvas.width = 540;   // Résolution interne haute qualité (3x plus haute)
    canvas.height = 540;  // Résolution interne haute qualité (3x plus haute)
    canvas.style.position = "absolute";
    canvas.style.left = "0";
    canvas.style.top = "0";
    canvas.style.width = "100%";   // S'adapter au conteneur
    canvas.style.height = "100%";  // S'adapter au conteneur
    container.appendChild(canvas);
    
    const ctx = canvas.getContext("2d");
    let time = 0;      // Temps total écoulé
    let lastTime = 0;  // Timestamp précédent

    // Configuration de la sphère 3D (mise à l'échelle pour haute résolution)
    const centerX = 540 / 2,  // Centre X du canvas (270px)
          centerY = 540 / 2;  // Centre Y du canvas (270px)
    
    const radius = 540 * 0.4, // Rayon de la sphère (40% de la largeur = 216px)
          numDots = 250,      // Nombre de points sur la sphère
          dots = [];          // Tableau des positions 3D
    
    // Générer les points uniformément répartis sur la sphère (algorithme de Fibonacci)
    for (let i = 0; i < numDots; i++) {
      // Calcul des angles sphériques pour répartition uniforme
      const theta = Math.acos(1 - 2 * (i / numDots));      // Angle polaire (0 à π)
      const phi = Math.sqrt(numDots * Math.PI) * theta;    // Angle azimutal (spirale dorée)
      
      // Conversion des coordonnées sphériques en cartésiennes 3D
      dots.push({
        x: radius * Math.sin(theta) * Math.cos(phi),  // Coordonnée X
        y: radius * Math.sin(theta) * Math.sin(phi),  // Coordonnée Y  
        z: radius * Math.cos(theta)                   // Coordonnée Z (profondeur)
      });
    }

    function animate(timestamp) {
      if (!lastTime) lastTime = timestamp;
      const deltaTime = timestamp - lastTime;
      lastTime = timestamp;
      time += deltaTime * 0.0005 * GLOBAL_SPEED;

      ctx.clearRect(0, 0, 540, 540);

      const rotX = Math.sin(time * 0.3) * 0.5,
        rotY = time * 0.5;
      const easedTime = easeInOutCubic((Math.sin(time * 2.5) + 1) / 2);
      const scanLine = (easedTime * 2 - 1) * radius,
        scanWidth = 75;  // Largeur du scanner mise à l'échelle (25 * 3)

      dots.forEach((dot) => {
        let { x, y, z } = dot;
        let nX = x * Math.cos(rotY) - z * Math.sin(rotY);
        let nZ = x * Math.sin(rotY) + z * Math.cos(rotY);
        x = nX;
        z = nZ;
        let nY = y * Math.cos(rotX) - z * Math.sin(rotX);
        nZ = y * Math.sin(rotX) + z * Math.cos(rotX);
        y = nY;
        z = nZ;
        const scale = (z + radius * 1.5) / (radius * 2.5);
        const pX = centerX + x,
          pY = centerY + y;
        const distToScan = Math.abs(y - scanLine);
        let scanInfluence =
          distToScan < scanWidth
            ? Math.cos((distToScan / scanWidth) * (Math.PI / 2))
            : 0;
        const size = Math.max(0, (scale * 2.0 + scanInfluence * 2.5) * 3);  // Taille mise à l'échelle
        const opacity = Math.max(0, scale * 0.6 + scanInfluence * 0.4);
        ctx.beginPath();
        ctx.arc(pX, pY, size, 0, Math.PI * 2);
        ctx.fillStyle = MONOCHROME_FILL(opacity);
        ctx.fill();
      });

      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  }

  // Animation "Radial Pulse" - Impulsions radiales du centre vers l'extérieur
  // Destinée à la carte "PCI Helper"
  function setupRadialPulse() {
    // Sélectionner le conteneur spécifique dans la carte helper
    const container = document.querySelector(".card-helper .white-container");
    if (!container) return;  // Protection contre les erreurs
    
    // Créer un canvas avec une résolution haute pour une meilleure qualité
    container.innerHTML = "";
    const canvas = document.createElement("canvas");
    canvas.width = 540;   // Résolution interne haute qualité (3x plus haute)
    canvas.height = 540;  // Résolution interne haute qualité (3x plus haute)
    canvas.style.position = "absolute";
    canvas.style.left = "0";
    canvas.style.top = "0";
    canvas.style.width = "100%";   // S'adapter au conteneur
    canvas.style.height = "100%";  // S'adapter au conteneur
    container.appendChild(canvas);
    
    const ctx = canvas.getContext("2d");
    const centerX = canvas.width / 2;   // Centre X (270px)
    const centerY = canvas.height / 2;  // Centre Y (270px)
    const maxRadius = 225;              // Rayon maximum des impulsions (75 * 3)
    let time = 0;      // Temps total écoulé
    let lastTime = 0;  // Timestamp précédent
    
    // Configuration des anneaux d'impulsion
    const ringCount = 8;        // Nombre d'anneaux simultanés
    const dotsPerRing = 12;     // Nombre de points par anneau
    const pulseSpeed = 0.35;    // Vitesse des impulsions (réduite pour fluidité)

    function animate(timestamp) {
      if (!lastTime) lastTime = timestamp;
      const deltaTime = timestamp - lastTime;
      lastTime = timestamp;
      time += deltaTime * 0.001;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw central dot (mise à l'échelle)
      ctx.beginPath();
      ctx.arc(centerX, centerY, 9, 0, Math.PI * 2);  // 3 * 3 = 9px
      ctx.fillStyle = "rgba(0, 0, 0, 0.9)";
      ctx.fill();
      
      // Pulse wave effect - creates waves of dots moving outward
      for (let i = 0; i < ringCount; i++) {
        // Calculate current radius for this ring
        // This creates a repeating pulse effect from center to edge
        const pulsePhase = (time * pulseSpeed + i / ringCount) % 1;
        const ringRadius = pulsePhase * maxRadius;
        
        // Skip rings that are just starting (too close to center)
        if (ringRadius < 15) continue;  // Seuil mis à l'échelle (5 * 3)
        
        // Opacity decreases as the pulse moves outward
        const opacity = 1 - pulsePhase;
        
        // Draw dots around the ring
        for (let j = 0; j < dotsPerRing; j++) {
          const angle = (j / dotsPerRing) * Math.PI * 2;
          const x = centerX + Math.cos(angle) * ringRadius;
          const y = centerY + Math.sin(angle) * ringRadius;
          
          // Dot size decreases as the pulse moves outward (mise à l'échelle)
          const dotSize = 7.5 * (1 - pulsePhase * 0.5);  // 2.5 * 3 = 7.5
          
          ctx.beginPath();
          ctx.arc(x, y, dotSize, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(0, 0, 0, ${opacity})`;
          ctx.fill();
        }
      }
      
      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  }

  // Initialisation des animations au chargement de la page
  window.addEventListener("load", function () {
    console.log("Page loaded, setting up animations");
    
    // Délai de 500ms pour s'assurer que tous les éléments DOM sont rendus
    // et que les styles CSS sont appliqués avant de créer les canvas
    setTimeout(() => {
      console.log("Setting up animations");
      
      // Initialiser les trois animations dans leurs cartes respectives
      setupHelixScanner();   // Animation pour la carte PCI Scraper
      setup3DSphereScan();   // Animation pour la carte PCI Converter  
      setupRadialPulse();    // Animation pour la carte PCI Helper
    }, 500);
  });
})();  // Fin du module auto-exécuté