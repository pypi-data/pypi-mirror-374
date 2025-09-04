/**
 * AxiomTradeAPI-py Documentation Website
 * Interactive JavaScript Features
 */

// ===== MAIN APPLICATION CLASS =====
class AxiomDocsApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupNavigation();
        this.setupTabs();
        this.setupAPINavigation();
        this.setupCodeExamples();
        this.setupModals();
        this.setupScrollEffects();
        this.setupCopyButtons();
        this.setupBackToTop();
        this.setupMobileMenu();
        this.initializeAnimations();
    }

    // ===== EVENT LISTENERS =====
    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    this.smoothScrollTo(target);
                }
            });
        });

        // Handle window resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));

        // Handle scroll events
        window.addEventListener('scroll', this.throttle(() => {
            this.handleScroll();
        }, 16));

        // Handle keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
    }

    // ===== NAVIGATION =====
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('section[id]');

        // Update active nav link based on scroll position
        this.updateActiveNavLink = () => {
            const scrollPos = window.scrollY + 100;
            
            sections.forEach(section => {
                const top = section.getBoundingClientRect().top + window.scrollY;
                const bottom = top + section.offsetHeight;
                const id = section.getAttribute('id');
                const link = document.querySelector(`a[href="#${id}"]`);

                if (scrollPos >= top && scrollPos < bottom) {
                    navLinks.forEach(l => l.classList.remove('active'));
                    if (link) link.classList.add('active');
                }
            });
        };

        // Navbar background on scroll
        this.updateNavbarBackground = () => {
            const navbar = document.getElementById('navbar');
            if (window.scrollY > 50) {
                navbar.style.background = 'var(--bg-overlay)';
                navbar.style.backdropFilter = 'blur(10px)';
            } else {
                navbar.style.background = 'transparent';
                navbar.style.backdropFilter = 'none';
            }
        };
    }

    // ===== TABS SYSTEM =====
    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.getAttribute('data-tab');
                
                // Remove active class from all buttons and panes
                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));
                
                // Add active class to clicked button and corresponding pane
                btn.classList.add('active');
                const targetPane = document.getElementById(targetTab);
                if (targetPane) {
                    targetPane.classList.add('active');
                    this.animateTabContent(targetPane);
                }
            });
        });
    }

    animateTabContent(pane) {
        pane.style.opacity = '0';
        pane.style.transform = 'translateY(10px)';
        
        requestAnimationFrame(() => {
            pane.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
            pane.style.opacity = '1';
            pane.style.transform = 'translateY(0)';
        });
    }

    // ===== API NAVIGATION =====
    setupAPINavigation() {
        const apiNavBtns = document.querySelectorAll('.api-nav-btn');
        const apiSections = document.querySelectorAll('.api-section');

        apiNavBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetSection = btn.getAttribute('data-section');
                
                // Remove active class from all buttons and sections
                apiNavBtns.forEach(b => b.classList.remove('active'));
                apiSections.forEach(s => s.classList.remove('active'));
                
                // Add active class to clicked button and corresponding section
                btn.classList.add('active');
                const targetPane = document.getElementById(`api-${targetSection}`);
                if (targetPane) {
                    targetPane.classList.add('active');
                    this.animateAPIContent(targetPane);
                }
            });
        });
    }

    animateAPIContent(section) {
        section.style.opacity = '0';
        section.style.transform = 'translateY(10px)';
        
        requestAnimationFrame(() => {
            section.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        });
    }

    // ===== CODE EXAMPLES =====
    setupCodeExamples() {
        // Example code data
        this.exampleCodes = {
            portfolio: `import logging
from axiomtradeapi import AxiomTradeClient
from config import Config

class PortfolioTracker:
    def __init__(self):
        self.client = AxiomTradeClient(log_level=logging.INFO)
        logger.info("✅ Portfolio tracker initialized")
    
    def check_multiple_wallets(self, wallet_addresses):
        try:
            logger.info(f"🔍 Checking {len(wallet_addresses)} wallets...")
            
            # Use batch operation for efficiency
            balances = self.client.GetBatchedBalance(wallet_addresses)
            
            # Calculate portfolio metrics
            total_sol = 0
            active_wallets = 0
            
            for address, balance_data in balances.items():
                if balance_data:
                    sol_amount = balance_data['sol']
                    total_sol += sol_amount
                    active_wallets += 1
            
            print(f"Total SOL: {total_sol:.6f}")
            return balances
            
        except Exception as e:
            logger.error(f"❌ Error checking portfolio: {e}")
            return None`,
            
            sniper: `import asyncio
from axiomtradeapi import AxiomTradeClient

class TokenSniperBot:
    def __init__(self):
        self.client = AxiomTradeClient(
            auth_token="your-auth-token",
            refresh_token="your-refresh-token"
        )
        self.min_market_cap = 5.0     # Minimum 5 SOL market cap
        self.min_liquidity = 10.0     # Minimum 10 SOL liquidity
        
    async def handle_new_tokens(self, tokens):
        for token in tokens:
            # Basic token info
            token_name = token.get('tokenName', 'Unknown')
            market_cap = token.get('marketCapSol', 0)
            liquidity = token.get('liquiditySol', 0)
            
            # Check if token meets our criteria
            if (market_cap >= self.min_market_cap and 
                liquidity >= self.min_liquidity):
                
                print(f"🎯 QUALIFIED TOKEN: {token_name}")
                print(f"   Market Cap: {market_cap:.2f} SOL")
                print(f"   Liquidity: {liquidity:.2f} SOL")
                
                await self.analyze_token_opportunity(token)
    
    async def start_monitoring(self):
        await self.client.subscribe_new_tokens(self.handle_new_tokens)
        await self.client.ws.start()`,
            
            arbitrage: `import asyncio
from axiomtradeapi import AxiomTradeClient

class ArbitrageScanner:
    def __init__(self):
        self.client = AxiomTradeClient(
            auth_token="your-auth-token",
            refresh_token="your-refresh-token"
        )
        self.min_profit_threshold = 0.005  # 0.5% minimum profit
        self.max_position_size = 1.0       # Max 1 SOL per trade
        
    async def scan_for_opportunities(self):
        # Get token prices from multiple DEXs
        raydium_prices = await self.get_raydium_prices()
        orca_prices = await self.get_orca_prices()
        
        opportunities = []
        
        for token_address in raydium_prices:
            if token_address in orca_prices:
                raydium_price = raydium_prices[token_address]
                orca_price = orca_prices[token_address]
                
                # Calculate potential profit
                price_diff = abs(raydium_price - orca_price)
                profit_pct = price_diff / min(raydium_price, orca_price)
                
                if profit_pct > self.min_profit_threshold:
                    opportunity = {
                        'token': token_address,
                        'raydium_price': raydium_price,
                        'orca_price': orca_price,
                        'profit_pct': profit_pct,
                        'estimated_profit': self.calculate_profit(price_diff)
                    }
                    opportunities.append(opportunity)
                    
        return sorted(opportunities, key=lambda x: x['profit_pct'], reverse=True)
    
    async def execute_arbitrage(self, opportunity):
        # Risk management checks
        if not self.validate_opportunity(opportunity):
            return False
            
        # Execute the arbitrage trade
        print(f"🚀 Executing arbitrage for {opportunity['token']}")
        print(f"   Expected profit: {opportunity['profit_pct']:.2%}")
        
        # Implementation would go here
        return True`
        };

        // Setup view code buttons
        const viewCodeBtns = document.querySelectorAll('.view-code-btn');
        viewCodeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const exampleType = btn.getAttribute('data-example');
                this.showCodeModal(exampleType);
            });
        });
    }

    showCodeModal(exampleType) {
        const modal = document.getElementById('code-modal');
        const modalTitle = document.getElementById('modal-title');
        const codeTitle = document.getElementById('code-title');
        const modalCode = document.getElementById('modal-code');
        const modalCopyBtn = document.getElementById('modal-copy-btn');

        const titles = {
            portfolio: 'Portfolio Tracker Example',
            sniper: 'Token Sniper Bot Example',
            arbitrage: 'Arbitrage Scanner Example'
        };

        modalTitle.textContent = titles[exampleType] || 'Code Example';
        codeTitle.textContent = titles[exampleType] || 'Example Code';
        modalCode.textContent = this.exampleCodes[exampleType] || '';

        // Update copy button
        modalCopyBtn.setAttribute('data-copy', this.exampleCodes[exampleType] || '');

        // Show modal
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';

        // Highlight syntax
        if (window.Prism) {
            Prism.highlightElement(modalCode);
        }
    }

    // ===== MODALS =====
    setupModals() {
        const modal = document.getElementById('code-modal');
        const closeBtn = document.getElementById('modal-close');

        // Close modal when clicking close button
        closeBtn.addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.closeModal();
            }
        });
    }

    closeModal() {
        const modal = document.getElementById('code-modal');
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }

    // ===== COPY BUTTONS =====
    setupCopyButtons() {
        const copyBtns = document.querySelectorAll('.copy-btn');
        
        copyBtns.forEach(btn => {
            btn.addEventListener('click', async () => {
                const textToCopy = btn.getAttribute('data-copy');
                
                try {
                    await navigator.clipboard.writeText(textToCopy);
                    this.showCopyFeedback(btn, 'Copied!');
                } catch (err) {
                    // Fallback for older browsers
                    this.fallbackCopy(textToCopy);
                    this.showCopyFeedback(btn, 'Copied!');
                }
            });
        });
    }

    showCopyFeedback(btn, message) {
        const originalHTML = btn.innerHTML;
        btn.innerHTML = `<i class="fas fa-check"></i> ${message}`;
        btn.style.background = 'var(--success-color)';
        
        setTimeout(() => {
            btn.innerHTML = originalHTML;
            btn.style.background = '';
        }, 2000);
    }

    fallbackCopy(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Fallback copy failed', err);
        }
        
        document.body.removeChild(textArea);
    }

    // ===== SCROLL EFFECTS =====
    setupScrollEffects() {
        // Intersection Observer for animations
        this.observeElements();
        
        // Parallax effects
        this.setupParallax();
    }

    observeElements() {
        const animateElements = document.querySelectorAll(
            '.feature-card, .doc-item, .example-card, .community-card, .method-card'
        );

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animateElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            observer.observe(el);
        });
    }

    setupParallax() {
        const parallaxElements = document.querySelectorAll('.hero-particles');
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            
            parallaxElements.forEach(el => {
                el.style.transform = `translateY(${rate}px)`;
            });
        });
    }

    // ===== BACK TO TOP =====
    setupBackToTop() {
        const backToTopBtn = document.getElementById('back-to-top');
        
        backToTopBtn.addEventListener('click', () => {
            this.smoothScrollTo(document.body);
        });
    }

    // ===== MOBILE MENU =====
    setupMobileMenu() {
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');
        
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close menu when clicking nav links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
    }

    // ===== SCROLL HANDLING =====
    handleScroll() {
        this.updateActiveNavLink();
        this.updateNavbarBackground();
        this.updateBackToTopButton();
    }

    updateBackToTopButton() {
        const backToTopBtn = document.getElementById('back-to-top');
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    }

    // ===== ANIMATIONS =====
    initializeAnimations() {
        // Counter animation for hero stats
        this.animateCounters();
        
        // Typing animation for hero title
        this.setupTypingAnimation();
    }

    animateCounters() {
        const counters = document.querySelectorAll('.stat-number');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        counters.forEach(counter => observer.observe(counter));
    }

    animateCounter(element) {
        const target = element.textContent;
        const isPercentage = target.includes('%');
        const isTime = target.includes('ms');
        const isNumber = target.includes('+');
        
        let finalValue = parseFloat(target.replace(/[^\d.]/g, ''));
        let current = 0;
        const increment = finalValue / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= finalValue) {
                current = finalValue;
                clearInterval(timer);
            }
            
            let displayValue = Math.floor(current);
            if (isTime) {
                element.textContent = `< ${displayValue}ms`;
            } else if (isPercentage) {
                element.textContent = `${(current).toFixed(1)}%`;
            } else if (isNumber) {
                element.textContent = `${displayValue}+`;
            } else {
                element.textContent = displayValue;
            }
        }, 30);
    }

    setupTypingAnimation() {
        const typingElement = document.querySelector('.gradient-text');
        if (!typingElement) return;

        const originalText = typingElement.textContent;
        typingElement.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < originalText.length) {
                typingElement.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };

        // Start typing animation after a delay
        setTimeout(typeWriter, 1000);
    }

    // ===== UTILITY FUNCTIONS =====
    smoothScrollTo(target) {
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition - 80; // Account for navbar
        const duration = 800;
        let start = null;

        const step = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            const percent = Math.min(progress / duration, 1);
            
            // Easing function
            const ease = percent < 0.5 
                ? 2 * percent * percent 
                : 1 - Math.pow(-2 * percent + 2, 2) / 2;
            
            window.scrollTo(0, startPosition + distance * ease);
            
            if (progress < duration) {
                requestAnimationFrame(step);
            }
        };

        requestAnimationFrame(step);
    }

    handleResize() {
        // Handle responsive changes
        this.updateLayout();
    }

    updateLayout() {
        // Update layout calculations on resize
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            this.enableMobileOptimizations();
        } else {
            this.disableMobileOptimizations();
        }
    }

    enableMobileOptimizations() {
        // Mobile-specific optimizations
        const parallaxElements = document.querySelectorAll('.hero-particles');
        parallaxElements.forEach(el => {
            el.style.transform = 'none';
        });
    }

    disableMobileOptimizations() {
        // Desktop optimizations
    }

    handleKeyboardNavigation(e) {
        // Handle keyboard shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'k':
                    e.preventDefault();
                    // Focus search if implemented
                    break;
                case '/':
                    e.preventDefault();
                    // Toggle search if implemented
                    break;
            }
        }

        // Handle escape key
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                this.closeModal();
            }
        }
    }

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// ===== ADDITIONAL UTILITIES =====

// Theme switcher (if needed)
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.setupToggleButton();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(this.currentTheme);
    }

    setupToggleButton() {
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }
}

// Search functionality (if needed)
class SearchManager {
    constructor() {
        this.searchIndex = [];
        this.init();
    }

    init() {
        this.buildSearchIndex();
        this.setupSearchInput();
    }

    buildSearchIndex() {
        // Build search index from content
        const searchableElements = document.querySelectorAll(
            'h1, h2, h3, h4, p, .doc-title, .feature-title, .method-name'
        );

        searchableElements.forEach(el => {
            this.searchIndex.push({
                text: el.textContent,
                element: el,
                type: el.tagName.toLowerCase()
            });
        });
    }

    search(query) {
        if (!query || query.length < 2) return [];

        const results = this.searchIndex.filter(item =>
            item.text.toLowerCase().includes(query.toLowerCase())
        );

        return results.slice(0, 10); // Limit results
    }

    setupSearchInput() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const results = this.search(e.target.value);
                this.displaySearchResults(results);
            });
        }
    }

    displaySearchResults(results) {
        // Display search results
        console.log('Search results:', results);
    }
}

// Performance monitor
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        this.measurePageLoad();
        this.monitorInteractions();
    }

    measurePageLoad() {
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            this.metrics.pageLoad = {
                domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                firstPaint: this.getFirstPaint()
            };
        });
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    monitorInteractions() {
        // Monitor user interactions for performance insights
        let interactionCount = 0;
        
        document.addEventListener('click', () => {
            interactionCount++;
        });

        // Report metrics periodically
        setInterval(() => {
            if (interactionCount > 0) {
                console.log('Performance metrics:', {
                    ...this.metrics,
                    interactions: interactionCount
                });
                interactionCount = 0;
            }
        }, 30000); // Every 30 seconds
    }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main application
    window.axiomApp = new AxiomDocsApp();
    
    // Initialize additional managers if needed
    // window.themeManager = new ThemeManager();
    // window.searchManager = new SearchManager();
    // window.performanceMonitor = new PerformanceMonitor();
    
    console.log('AxiomTradeAPI-py Documentation Website initialized');
});

// Service Worker registration (if available)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}