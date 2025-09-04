// FixieRun PWA - Progressive Web App for Web3 Fitness
// Complete functionality with offline support and blockchain simulation

class FixieRunApp {
  constructor() {
    this.currentScreen = 'home';
    this.isTracking = false;
    this.isPaused = false;
    this.startTime = null;
    this.totalTime = 0;
    this.distance = 0;
    this.calories = 0;
    this.tokens = 0;
    this.speed = 0;
    this.currentWorkout = null;
    this.theme = 'dark';
    
    // Initialize app data
    this.userData = {
      id: "user_123",
      name: "Alex",
      level: 12,
      experience: 2450,
      experienceToNextLevel: 3000,
      streakDays: 7,
      weeklyDistance: 32.5,
      weeklyCalories: 1250,
      tokenBalance: 125.75,
      walletAddress: "0x1234...5678",
      profileImage: null
    };
    
    this.workouts = [
      {
        id: 1,
        name: "Urban Sprint",
        type: "fixie",
        intensity: "High",
        duration: "25 min",
        calories: 350,
        description: "High-intensity sprint training through urban areas"
      },
      {
        id: 2,
        name: "Endurance Ride",
        type: "fixie",
        intensity: "Medium",
        duration: "45 min",
        calories: 420,
        description: "Long-distance endurance training to build stamina"
      },
      {
        id: 3,
        name: "City Explorer",
        type: "fixie",
        intensity: "Low",
        duration: "60 min",
        calories: 380,
        description: "Exploration ride through city landmarks"
      },
      {
        id: 4,
        name: "Interval Run",
        type: "running",
        intensity: "High",
        duration: "30 min",
        calories: 400,
        description: "Alternating between sprinting and jogging"
      },
      {
        id: 5,
        name: "Steady Jog",
        type: "running",
        intensity: "Medium",
        duration: "40 min",
        calories: 350,
        description: "Consistent pace running to build endurance"
      }
    ];
    
    this.nfts = [
      {
        id: 1,
        name: "Neon Racer",
        rarity: "Rare",
        level: 3,
        boost: "+5% XP",
        description: "A rare NFT sneaker with enhanced performance"
      },
      {
        id: 2,
        name: "Urban Phantom",
        rarity: "Uncommon",
        level: 2,
        boost: "+2% Tokens",
        description: "Sleek urban design for city runners"
      },
      {
        id: 3,
        name: "Street King",
        rarity: "Common",
        level: 1,
        boost: "+1% Speed",
        description: "Entry-level NFT with basic benefits"
      }
    ];
    
    this.init();
  }
  
  async init() {
    // Show loading screen
    this.showLoadingScreen();
    
    // Initialize PWA features
    await this.initPWA();
    
    // Initialize theme
    this.initTheme();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Load saved data
    this.loadData();
    
    // Initialize screens
    this.initializeScreens();
    
    // Hide loading screen and show app
    setTimeout(() => {
      this.hideLoadingScreen();
      this.navigateToScreen('home'); // Ensure we start on home screen
    }, 2000);
    
    // Check for updates
    this.checkForUpdates();
  }
  
  initializeScreens() {
    // Make sure all screens are hidden except home
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => {
      screen.classList.remove('active');
    });
    
    // Show home screen by default
    const homeScreen = document.getElementById('home-screen');
    if (homeScreen) {
      homeScreen.classList.add('active');
    }
    
    // Make sure bottom nav is visible
    const bottomNav = document.querySelector('.bottom-nav');
    if (bottomNav) {
      bottomNav.style.display = 'flex';
    }
  }
  
  async initPWA() {
    // Register Service Worker
    if ('serviceWorker' in navigator) {
      try {
        // Create inline service worker
        const swCode = `
          const CACHE_NAME = 'fixierun-v1';
          const urlsToCache = [
            '/',
            '/index.html',
            '/style.css',
            '/app.js'
          ];
          
          self.addEventListener('install', event => {
            event.waitUntil(
              caches.open(CACHE_NAME)
                .then(cache => cache.addAll(urlsToCache))
            );
          });
          
          self.addEventListener('fetch', event => {
            event.respondWith(
              caches.match(event.request)
                .then(response => {
                  if (response) {
                    return response;
                  }
                  return fetch(event.request);
                })
            );
          });
        `;
        
        const blob = new Blob([swCode], { type: 'application/javascript' });
        const swUrl = URL.createObjectURL(blob);
        
        const registration = await navigator.serviceWorker.register(swUrl);
        console.log('SW registered: ', registration);
        
        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });
      } catch (error) {
        console.log('SW registration failed: ', error);
      }
    }
    
    // Handle app install
    this.setupInstallPrompt();
    
    // Handle offline/online events
    this.setupOfflineHandling();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }
  
  setupInstallPrompt() {
    let deferredPrompt;
    
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      
      // Show install button
      this.showInstallButton(deferredPrompt);
    });
    
    window.addEventListener('appinstalled', () => {
      console.log('App was installed');
      deferredPrompt = null;
    });
  }
  
  showInstallButton(deferredPrompt) {
    // Add install button to header if not already present
    const headerActions = document.querySelector('.header-actions');
    if (!document.querySelector('.install-btn')) {
      const installBtn = document.createElement('button');
      installBtn.className = 'btn-icon install-btn';
      installBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7,10 12,15 17,10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      `;
      installBtn.addEventListener('click', () => {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            installBtn.remove();
          }
          deferredPrompt = null;
        });
      });
      headerActions.insertBefore(installBtn, headerActions.firstChild);
    }
  }
  
  setupOfflineHandling() {
    const offlineIndicator = document.createElement('div');
    offlineIndicator.className = 'offline-indicator';
    offlineIndicator.textContent = 'You are currently offline. Some features may be limited.';
    document.body.appendChild(offlineIndicator);
    
    const updateOnlineStatus = () => {
      if (navigator.onLine) {
        offlineIndicator.classList.remove('show');
        // Sync data when back online
        this.syncData();
      } else {
        offlineIndicator.classList.add('show');
      }
    };
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Initial check
    updateOnlineStatus();
  }
  
  initTheme() {
    // Load saved theme or use system preference
    const savedTheme = localStorage.getItem('fixierun-theme');
    if (savedTheme) {
      this.theme = savedTheme;
    } else {
      this.theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    document.body.setAttribute('data-color-scheme', this.theme);
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('fixierun-theme')) {
        this.theme = e.matches ? 'dark' : 'light';
        document.body.setAttribute('data-color-scheme', this.theme);
      }
    });
  }
  
  setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        this.toggleTheme();
      });
    }
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const screen = e.currentTarget.dataset.screen;
        if (screen) {
          this.navigateToScreen(screen);
        }
      });
    });
    
    // Quick start workout
    const quickStartBtn = document.querySelector('.quick-start-btn');
    if (quickStartBtn) {
      quickStartBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.navigateToScreen('track');
      });
    }
    
    // Workout filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.filterWorkouts(e.target.dataset.filter);
      });
    });
    
    // Start workout buttons
    document.querySelectorAll('.start-workout-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const workoutId = parseInt(e.target.dataset.workoutId);
        this.startWorkoutFromList(workoutId);
      });
    });
    
    // Track screen controls
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (startBtn) {
      startBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.startTracking();
      });
    }
    
    if (pauseBtn) {
      pauseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.pauseTracking();
      });
    }
    
    if (stopBtn) {
      stopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.stopTracking();
      });
    }
    
    // Mode toggle
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.switchMode(e.target.dataset.mode);
      });
    });
    
    // Multiplayer toggle
    const multiplayerCheckbox = document.getElementById('multiplayer-checkbox');
    if (multiplayerCheckbox) {
      multiplayerCheckbox.addEventListener('change', (e) => {
        this.toggleMultiplayer(e.target.checked);
      });
    }
    
    // Token actions
    document.querySelectorAll('.token-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handleTokenAction(e.target.textContent.toLowerCase());
      });
    });
    
    // Modal close
    const closeModalBtn = document.getElementById('close-workout-modal');
    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.closeWorkoutModal();
      });
    }
    
    // Settings toggles
    document.querySelectorAll('.connection-toggle, .setting-toggle').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleSetting(e.currentTarget);
      });
    });
    
    // Logout
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.logout();
      });
    }
    
    // Logo click to go home
    const appLogo = document.querySelector('.app-logo');
    if (appLogo) {
      appLogo.addEventListener('click', (e) => {
        e.preventDefault();
        this.navigateToScreen('home');
      });
      appLogo.style.cursor = 'pointer';
    }
  }
  
  showLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    const app = document.getElementById('app');
    
    if (loadingScreen) {
      loadingScreen.style.display = 'flex';
    }
    if (app) {
      app.classList.add('hidden');
    }
  }
  
  hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    const app = document.getElementById('app');
    
    if (loadingScreen) {
      loadingScreen.style.display = 'none';
    }
    if (app) {
      app.classList.remove('hidden');
    }
  }
  
  toggleTheme() {
    this.theme = this.theme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-color-scheme', this.theme);
    localStorage.setItem('fixierun-theme', this.theme);
    
    // Animate theme icon
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
      themeIcon.style.transform = 'rotate(180deg)';
      setTimeout(() => {
        themeIcon.style.transform = 'rotate(0deg)';
      }, 300);
    }
  }
  
  navigateToScreen(screenName) {
    console.log('Navigating to screen:', screenName);
    
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
      screen.classList.remove('active');
    });
    
    // Show target screen
    const targetScreen = document.getElementById(`${screenName}-screen`);
    if (targetScreen) {
      targetScreen.classList.add('active');
    } else {
      console.error('Screen not found:', `${screenName}-screen`);
      return;
    }
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
    });
    
    const navItem = document.querySelector(`[data-screen="${screenName}"]`);
    if (navItem) {
      navItem.classList.add('active');
    }
    
    this.currentScreen = screenName;
    
    // Screen-specific initialization
    if (screenName === 'track') {
      this.resetTrackingState();
    } else if (screenName === 'home') {
      this.updateStatsDisplay();
    } else if (screenName === 'rewards') {
      this.updateRewardsDisplay();
    }
  }
  
  filterWorkouts(filter) {
    // Update filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`[data-filter="${filter}"]`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }
    
    // Filter workout cards
    document.querySelectorAll('.workout-card').forEach(card => {
      const cardType = card.dataset.type;
      if (filter === 'all' || filter === cardType) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }
  
  startWorkoutFromList(workoutId) {
    this.currentWorkout = this.workouts.find(w => w.id === workoutId);
    this.navigateToScreen('track');
    
    // Auto-start tracking after a brief delay
    setTimeout(() => {
      this.startTracking();
    }, 1000);
  }
  
  resetTrackingState() {
    this.isTracking = false;
    this.isPaused = false;
    this.startTime = null;
    this.totalTime = 0;
    this.distance = 0;
    this.calories = 0;
    this.tokens = 0;
    this.speed = 0;
    
    // Clear any existing intervals
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
      this.trackingInterval = null;
    }
    
    // Reset UI
    this.updateTrackingDisplay();
    this.updateTrackingControls();
  }
  
  startTracking() {
    this.isTracking = true;
    this.isPaused = false;
    this.startTime = Date.now() - this.totalTime;
    
    this.updateTrackingControls();
    
    // Start tracking loop
    this.trackingInterval = setInterval(() => {
      this.updateTrackingStats();
    }, 1000);
    
    // Request geolocation (simulated)
    this.simulateGPS();
    
    // Show notification
    this.showNotification('Workout Started', 'Your fitness journey begins now! 💪');
  }
  
  pauseTracking() {
    this.isPaused = true;
    this.totalTime = Date.now() - this.startTime;
    
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
    }
    this.updateTrackingControls();
    
    const timerStatus = document.querySelector('.timer-status');
    if (timerStatus) {
      timerStatus.textContent = 'Paused';
    }
  }
  
  stopTracking() {
    this.isTracking = false;
    this.isPaused = false;
    
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
    }
    
    // Calculate final stats
    const finalStats = {
      distance: this.distance,
      calories: this.calories,
      tokens: this.tokens,
      duration: this.formatTime(this.totalTime)
    };
    
    // Show completion modal
    this.showWorkoutComplete(finalStats);
    
    // Add to activity history
    this.addActivityToHistory(finalStats);
    
    // Update user stats
    this.updateUserStats(finalStats);
    
    this.resetTrackingState();
  }
  
  updateTrackingStats() {
    if (!this.isTracking || this.isPaused) return;
    
    this.totalTime = Date.now() - this.startTime;
    
    // Simulate movement (random but realistic values)
    const speedVariation = (Math.random() - 0.5) * 2; // -1 to 1 km/h variation
    const currentMode = document.querySelector('.mode-btn.active')?.dataset.mode || 'run';
    const baseSpeed = currentMode === 'bike' ? 18 : 8; // km/h
    
    this.speed = Math.max(0, baseSpeed + speedVariation);
    this.distance += (this.speed / 3600); // Convert to km per second
    
    // Calculate calories (rough estimation)
    const caloriesPerKm = currentMode === 'bike' ? 30 : 60;
    this.calories = Math.round(this.distance * caloriesPerKm);
    
    // Calculate tokens (distance-based reward)
    this.tokens = parseFloat((this.distance * 0.5).toFixed(2));
    
    this.updateTrackingDisplay();
  }
  
  updateTrackingDisplay() {
    // Update timer
    const timerTime = document.querySelector('.timer-time');
    const timerStatus = document.querySelector('.timer-status');
    
    if (timerTime) {
      timerTime.textContent = this.formatTime(this.totalTime);
    }
    if (timerStatus) {
      timerStatus.textContent = 
        this.isTracking ? (this.isPaused ? 'Paused' : 'Active') : 'Ready to start';
    }
    
    // Update live stats
    const distanceStat = document.querySelector('.live-stats .live-stat:nth-child(1) .stat-value');
    const speedStat = document.querySelector('.live-stats .live-stat:nth-child(2) .stat-value');
    const caloriesStat = document.querySelector('.live-stats .live-stat:nth-child(3) .stat-value');
    
    if (distanceStat) distanceStat.textContent = this.distance.toFixed(1);
    if (speedStat) speedStat.textContent = this.speed.toFixed(1);
    if (caloriesStat) caloriesStat.textContent = this.calories.toString();
    
    // Update token progress
    const tokenProgress = Math.min(100, (this.tokens / 10) * 100); // Max 10 tokens for 100%
    const progressFill = document.querySelector('.token-progress-fill');
    const progressValue = document.querySelector('.progress-value');
    
    if (progressFill) {
      progressFill.style.width = `${tokenProgress}%`;
    }
    if (progressValue) {
      progressValue.textContent = `${this.tokens} $FIXIE`;
    }
  }
  
  updateTrackingControls() {
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (startBtn && pauseBtn && stopBtn) {
      if (this.isTracking && !this.isPaused) {
        startBtn.classList.add('hidden');
        pauseBtn.classList.remove('hidden');
        stopBtn.classList.remove('hidden');
      } else if (this.isPaused) {
        startBtn.classList.remove('hidden');
        startBtn.textContent = 'Resume';
        pauseBtn.classList.add('hidden');
        stopBtn.classList.remove('hidden');
      } else {
        startBtn.classList.remove('hidden');
        startBtn.textContent = 'Start';
        pauseBtn.classList.add('hidden');
        stopBtn.classList.add('hidden');
      }
    }
  }
  
  formatTime(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  
  simulateGPS() {
    // Simulate GPS tracking with realistic movement
    const mapInfo = document.querySelector('.map-info');
    if (mapInfo) {
      mapInfo.textContent = 'Route tracking active...';
    }
    
    // Change map background to simulate movement
    let colorIndex = 0;
    const colors = ['#1FB8CD', '#FFC185', '#B4413C', '#5D878F'];
    
    const mapSimulation = setInterval(() => {
      if (this.isTracking && !this.isPaused) {
        const mapPlaceholder = document.querySelector('.map-placeholder');
        if (mapPlaceholder) {
          mapPlaceholder.style.backgroundColor = colors[colorIndex % colors.length];
          colorIndex++;
        }
      } else {
        clearInterval(mapSimulation);
      }
    }, 5000);
  }
  
  switchMode(mode) {
    // Update mode buttons
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    
    const activeBtn = document.querySelector(`[data-mode="${mode}"]`);
    if (activeBtn) {
      activeBtn.classList.add('active');
    }
    
    // Reset stats when switching mode if not tracking
    if (!this.isTracking) {
      this.resetTrackingState();
    }
  }
  
  toggleMultiplayer(enabled) {
    const mapOverlay = document.querySelector('.map-overlay');
    if (mapOverlay) {
      const existingIndicator = mapOverlay.querySelector('.multiplayer-indicator');
      if (existingIndicator) {
        existingIndicator.remove();
      }
      
      if (enabled) {
        const indicator = document.createElement('div');
        indicator.className = 'multiplayer-indicator';
        indicator.style.cssText = `
          position: absolute;
          top: 20px;
          right: 20px;
          color: #00ffff;
          font-size: 12px;
          background: rgba(0, 0, 0, 0.5);
          padding: 4px 8px;
          border-radius: 4px;
        `;
        indicator.textContent = '👥 2 users nearby';
        mapOverlay.appendChild(indicator);
      }
    }
  }
  
  showWorkoutComplete(stats) {
    const modal = document.getElementById('workout-complete-modal');
    
    if (modal) {
      // Update completion stats
      const distanceValue = document.querySelector('.completion-stat:nth-child(1) .stat-value');
      const caloriesValue = document.querySelector('.completion-stat:nth-child(2) .stat-value');
      const tokensValue = document.querySelector('.completion-stat:nth-child(3) .stat-value');
      
      if (distanceValue) distanceValue.textContent = stats.distance.toFixed(1);
      if (caloriesValue) caloriesValue.textContent = stats.calories.toString();
      if (tokensValue) tokensValue.textContent = stats.tokens.toString();
      
      modal.classList.remove('hidden');
      
      // Add celebration animation
      this.celebrateCompletion();
    }
  }
  
  closeWorkoutModal() {
    const modal = document.getElementById('workout-complete-modal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }
  
  celebrateCompletion() {
    // Simple celebration effect
    const modal = document.querySelector('.modal-content');
    if (modal) {
      modal.style.animation = 'pulse 0.6s ease-in-out';
      setTimeout(() => {
        modal.style.animation = '';
      }, 600);
    }
    
    // Show notification
    this.showNotification('Workout Complete! 🎉', `You earned ${this.tokens} $FIXIE tokens!`);
  }
  
  addActivityToHistory(stats) {
    // Add to local storage or simulate API call
    const activity = {
      date: new Date().toLocaleDateString(),
      type: this.currentWorkout ? this.currentWorkout.name : 'Quick Workout',
      distance: stats.distance,
      duration: stats.duration,
      calories: stats.calories,
      tokens: stats.tokens
    };
    
    console.log('Activity added:', activity);
  }
  
  updateUserStats(stats) {
    // Update user data
    this.userData.tokenBalance += stats.tokens;
    this.userData.weeklyDistance += stats.distance;
    this.userData.weeklyCalories += stats.calories;
    this.userData.experience += 150; // Fixed XP gain
    
    // Update displays
    this.updateStatsDisplay();
    this.updateRewardsDisplay();
    this.saveData();
  }
  
  updateStatsDisplay() {
    // Update home screen stats
    const distanceCard = document.querySelector('.stat-card:nth-child(1) .stat-value');
    const caloriesCard = document.querySelector('.stat-card:nth-child(2) .stat-value');
    const tokensCard = document.querySelector('.stat-card:nth-child(3) .stat-value');
    
    if (distanceCard) distanceCard.textContent = `${this.userData.weeklyDistance.toFixed(1)}km`;
    if (caloriesCard) caloriesCard.textContent = this.userData.weeklyCalories.toLocaleString();
    if (tokensCard) tokensCard.textContent = this.userData.tokenBalance.toFixed(2);
    
    // Update profile XP
    const xpProgress = (this.userData.experience / this.userData.experienceToNextLevel) * 100;
    const xpProgressBar = document.querySelector('.xp-progress .progress-fill');
    const xpValue = document.querySelector('.xp-value');
    
    if (xpProgressBar) xpProgressBar.style.width = `${xpProgress}%`;
    if (xpValue) xpValue.textContent = `${this.userData.experience} / ${this.userData.experienceToNextLevel} XP`;
  }
  
  updateRewardsDisplay() {
    // Update rewards screen token balance
    const balanceAmount = document.querySelector('.balance-amount');
    const balanceUsd = document.querySelector('.balance-usd');
    
    if (balanceAmount) balanceAmount.textContent = `${this.userData.tokenBalance.toFixed(2)} $FIXIE`;
    if (balanceUsd) balanceUsd.textContent = `≈ $${(this.userData.tokenBalance * 0.75).toFixed(2)} USD`;
  }
  
  handleTokenAction(action) {
    // Simulate blockchain transactions
    const actions = {
      buy: () => this.showNotification('Buy Order', 'Redirecting to exchange...'),
      sell: () => this.showNotification('Sell Order', 'Preparing transaction...'),
      transfer: () => this.showNotification('Transfer', 'Enter recipient address...')
    };
    
    if (actions[action]) {
      actions[action]();
    }
  }
  
  toggleSetting(element) {
    const toggle = element.querySelector('.toggle-switch');
    if (toggle) {
      toggle.classList.toggle('active');
      
      // Simulate setting change
      const settingName = element.previousElementSibling?.querySelector('.setting-name')?.textContent ||
                         element.previousElementSibling?.querySelector('.app-name')?.textContent;
      
      const isActive = toggle.classList.contains('active');
      this.showNotification('Settings Updated', `${settingName}: ${isActive ? 'Enabled' : 'Disabled'}`);
    }
  }
  
  logout() {
    if (confirm('Are you sure you want to logout?')) {
      // Clear user session
      localStorage.removeItem('fixierun-user-data');
      
      // Reset to initial state
      this.resetAppState();
      
      // Show loading screen briefly
      this.showLoadingScreen();
      setTimeout(() => {
        this.hideLoadingScreen();
        this.navigateToScreen('home');
      }, 1000);
    }
  }
  
  resetAppState() {
    this.resetTrackingState();
    this.navigateToScreen('home');
  }
  
  showNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: body,
        icon: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MjIiIGhlaWdodD0iNTIyIj48cmVjdCB3aWR0aD0iNTIyIiBoZWlnaHQ9IjUyMiIgZmlsbD0iIzVENUNERSIvPjwvc3ZnPg==',
        badge: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MjIiIGhlaWdodD0iNTIyIj48cmVjdCB3aWR0aT0iNTIyIiBoZWlnaHQ9IjUyMiIgZmlsbD0iIzVENUNERSIvPjwvc3ZnPg=='
      });
    } else {
      // Fallback: show in-app notification
      this.showInAppNotification(title, body);
    }
  }
  
  showInAppNotification(title, body) {
    const notification = document.createElement('div');
    notification.className = 'in-app-notification';
    notification.innerHTML = `
      <div class="notification-content">
        <strong>${title}</strong>
        <p>${body}</p>
      </div>
    `;
    
    notification.style.cssText = `
      position: fixed;
      top: 80px;
      right: 16px;
      background: var(--glass-background);
      backdrop-filter: var(--glass-backdrop);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-lg);
      padding: var(--space-16);
      color: var(--color-text);
      z-index: 1001;
      max-width: 300px;
      transform: translateX(100%);
      transition: transform var(--duration-normal) var(--ease-standard);
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 4000);
  }
  
  loadData() {
    // Load data from localStorage (simulating IndexedDB)
    const savedData = localStorage.getItem('fixierun-user-data');
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        Object.assign(this.userData, data);
        this.updateStatsDisplay();
      } catch (error) {
        console.error('Failed to load saved data:', error);
      }
    }
  }
  
  saveData() {
    // Save data to localStorage (simulating IndexedDB)
    try {
      localStorage.setItem('fixierun-user-data', JSON.stringify(this.userData));
    } catch (error) {
      console.error('Failed to save data:', error);
    }
  }
  
  syncData() {
    // Simulate data synchronization when back online
    console.log('Syncing data with server...');
    this.showNotification('Data Synced', 'Your progress has been saved to the blockchain.');
  }
  
  checkForUpdates() {
    // Simulate checking for app updates
    setTimeout(() => {
      if (Math.random() > 0.8) { // 20% chance to show update
        this.showUpdateNotification();
      }
    }, 10000);
  }
  
  showUpdateNotification() {
    const updateBanner = document.createElement('div');
    updateBanner.className = 'update-banner';
    updateBanner.innerHTML = `
      <div class="update-content">
        <span>New version available!</span>
        <button class="update-btn" onclick="location.reload()">Update Now</button>
      </div>
    `;
    
    updateBanner.style.cssText = `
      position: fixed;
      top: var(--header-height);
      left: 0;
      right: 0;
      background: var(--color-neon-purple);
      color: var(--color-white);
      padding: var(--space-12) var(--space-16);
      z-index: 99;
      display: flex;
      align-items: center;
      justify-content: space-between;
    `;
    
    document.body.appendChild(updateBanner);
  }
  
  // Background sync simulation
  requestBackgroundSync() {
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      navigator.serviceWorker.ready.then(registration => {
        return registration.sync.register('background-sync');
      }).catch(err => {
        console.log('Background sync registration failed:', err);
      });
    }
  }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing FixieRun app...');
  window.fixieRunApp = new FixieRunApp();
});

// Handle app visibility changes for better performance
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // App is in background
    if (window.fixieRunApp && window.fixieRunApp.isTracking) {
      // Continue tracking in background (limited functionality)
      console.log('App backgrounded during workout');
    }
  } else {
    // App is back in foreground
    if (window.fixieRunApp) {
      window.fixieRunApp.syncData();
    }
  }
});

// Handle app installation
window.addEventListener('appinstalled', () => {
  console.log('FixieRun PWA was installed');
  if (window.fixieRunApp) {
    window.fixieRunApp.showNotification('Welcome to FixieRun!', 'App installed successfully. Start your fitness journey!');
  }
});

// Performance optimization: Preload critical resources
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    // Preload images or other resources during idle time
    console.log('Preloading resources during idle time');
  });
}

// Add some CSS for dynamic notifications
const notificationStyles = `
  .in-app-notification {
    box-shadow: var(--shadow-lg);
  }
  
  .in-app-notification .notification-content strong {
    display: block;
    margin-bottom: var(--space-4);
    font-weight: var(--font-weight-semibold);
  }
  
  .in-app-notification .notification-content p {
    margin: 0;
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
  }
  
  .update-banner .update-btn {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: var(--color-white);
    padding: var(--space-4) var(--space-12);
    border-radius: var(--radius-base);
    font-size: var(--font-size-sm);
    cursor: pointer;
    transition: all var(--duration-fast) var(--ease-standard);
  }
  
  .update-banner .update-btn:hover {
    background: rgba(255, 255, 255, 0.3);
  }
  
  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
  }
`;

// Add the styles to the document
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);