// Auto-refresh stats every 30 seconds (prevent multiple intervals)
if (!window.statsRefreshInterval) {
    window.statsRefreshInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            // Update stats if they've changed
            updateStat('guilds', data.guilds);
            updateStat('users', data.users);
            updateStat('channels', data.channels);
            
            // Update uptime
            const uptimeStr = formatUptime(data.uptime_seconds);
            const uptimeElements = document.querySelectorAll('.stat-card:nth-child(4) .stat-value');
            uptimeElements.forEach(el => el.textContent = uptimeStr);
            
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        }
    }, 30000);
}

function updateStat(statName, value) {
    const statMap = {
        'guilds': 1,
        'users': 2,
        'channels': 3
    };
    
    const index = statMap[statName];
    const element = document.querySelector(`.stat-card:nth-child(${index}) .stat-value`);
    
    if (element && element.textContent !== value.toString()) {
        // Animate the change
        element.style.transform = 'scale(1.2)';
        element.style.color = '#ff006e';
        
        setTimeout(() => {
            element.textContent = value;
            element.style.transform = 'scale(1)';
            element.style.color = 'var(--neon-cyan)';
        }, 200);
    }
}

function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return `${days}d ${hours}h ${minutes}m ${secs}s`;
}

// Add scroll animations
document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    document.querySelectorAll('.stat-card, .feature-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
});

// Cyber grid effect on mouse move
document.addEventListener('mousemove', (e) => {
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    
    const stars = document.querySelector('.stars');
    const stars2 = document.querySelector('.stars2');
    const stars3 = document.querySelector('.stars3');
    
    if (stars) stars.style.transform = `translate(${x * 10}px, ${y * 10}px)`;
    if (stars2) stars2.style.transform = `translate(${x * 20}px, ${y * 20}px)`;
    if (stars3) stars3.style.transform = `translate(${x * 30}px, ${y * 30}px)`;
});

// Language translations
const translations = {
    en: {
        nav_dashboard: "Dashboard",
        nav_commands: "Commands",
        nav_support: "Support",
        nav_addbot: "Add Bot",
        view_all_commands: "View All Commands",
        subtitle: "Next-Gen Discord Moderation System",
        status_online: "SYSTEM ONLINE",
        active_servers: "Active Servers",
        total_users: "Total Users",
        active_channels: "Active Channels",
        system_uptime: "System Uptime",
        core_features: "CORE FEATURES",
        verification_title: "Verification System",
        verification_desc: "Anti-alt protection with button verification",
        ai_title: "AI Assistant",
        ai_desc: "OpenAI-powered chat responses",
        mod_title: "Advanced Moderation",
        mod_desc: "Ban, kick, timeout, warnings & more",
        music_title: "Music Player",
        music_desc: "🎥 YouTube • 🟢 Spotify • ☁️ SoundCloud",
        games_title: "Interactive Games",
        games_desc: "RPS, Tic-Tac-Toe & mini-games",
        multilang_title: "Multilingual",
        multilang_desc: "Full English & Hungarian support",
        slash_title: "48 Slash Commands",
        slash_desc: "! and / dual prefix support",
        quick_links: "QUICK LINKS",
        join_support: "Join Support Server",
        add_bot_server: "Add Bot to Server",
        meet_dev: "MEET THE DEVELOPER",
        owner_title: "Bot Owner & Creator",
        owner_desc: "Shadow-MOD is developed and maintained with passion to bring the next generation of Discord moderation to your servers. Built with cutting-edge technology and futuristic design, this bot combines powerful features with an intuitive user experience.",
        vision: "Vision",
        vision_desc: "Creating a futuristic Discord experience with AI-powered moderation, multilingual support, and seamless automation for communities worldwide.",
        powered_by: "Powered by Replit • Created with 💜",
        version: "Made by MoonlightVFX",
        help_title: "COMMAND DATABASE",
        help_subtitle: "Made by MoonlightVFX",
        cat_info: "INFORMATION SYSTEMS",
        cat_security: "SECURITY & VERIFICATION",
        cat_antialt: "ANTI-ALT SYSTEM",
        cat_mod: "MODERATION MATRIX",
        cat_tickets: "TICKET NEXUS",
        cat_games: "GAMING ARENA",
        cat_fun: "FUN PROTOCOLS",
        cat_polls: "POLL SYSTEM",
        cat_roles: "ROLE ARCHITECT",
        cat_giveaway: "GIVEAWAY ENGINE",
        cat_nameauto: "NAME AUTOMATION",
        cat_ai: "AI NEURAL LINK",
        cat_entertainment: "ENTERTAINMENT SYSTEMS",
        cat_engagement: "ENGAGEMENT PROTOCOLS",
        cat_language: "SYSTEM CONFIGURATION"
    },
    hu: {
        nav_dashboard: "Irányítópult",
        nav_commands: "Parancsok",
        nav_support: "Támogatás",
        nav_addbot: "Bot Hozzáadása",
        view_all_commands: "Összes Parancs Megtekintése",
        subtitle: "Következő Generációs Discord Moderációs Rendszer",
        status_online: "RENDSZER ONLINE",
        active_servers: "Aktív Szerverek",
        total_users: "Összes Felhasználó",
        active_channels: "Aktív Csatornák",
        system_uptime: "Rendszer Üzemidő",
        core_features: "ALAPVETŐ FUNKCIÓK",
        verification_title: "Ellenőrző Rendszer",
        verification_desc: "Anti-alt védelem gombos ellenőrzéssel",
        ai_title: "AI Asszisztens",
        ai_desc: "OpenAI-alapú chat válaszok",
        mod_title: "Fejlett Moderáció",
        mod_desc: "Kitiltás, kirúgás, timeout, figyelmeztetések",
        music_title: "Zene Lejátszó",
        music_desc: "🎥 YouTube • 🟢 Spotify • ☁️ SoundCloud",
        games_title: "Interaktív Játékok",
        games_desc: "Kő-Papír-Olló, Tic-Tac-Toe és mini játékok",
        multilang_title: "Többnyelvű",
        multilang_desc: "Teljes angol és magyar támogatás",
        slash_title: "48 Slash Parancs",
        slash_desc: "! és / dupla prefix támogatás",
        quick_links: "GYORS LINKEK",
        join_support: "Csatlakozz a Támogatói Szerverhez",
        add_bot_server: "Bot Hozzáadása Szerverhez",
        meet_dev: "ISMERD MEG A FEJLESZTŐT",
        owner_title: "Bot Tulajdonos és Készítő",
        owner_desc: "A Shadow-MOD szenvedéllyel van fejlesztve és karbantartva, hogy a Discord moderáció következő generációját hozza el szervereidre. Élvonalbeli technológiával és futurisztikus dizájnnal épült, ez a bot erőteljes funkciókat kombinál intuitív felhasználói élménnyel.",
        vision: "Jövőkép",
        vision_desc: "Futurisztikus Discord élmény megteremtése AI-alapú moderációval, többnyelvű támogatással és zökkenőmentes automatizálással közösségek számára világszerte.",
        powered_by: "Powered by Replit • Készítve 💜-tel",
        version: "MoonlightVFX által készítve",
        help_title: "PARANCSADATBÁZIS",
        help_subtitle: "MoonlightVFX által készítve",
        cat_info: "INFORMÁCIÓS RENDSZEREK",
        cat_security: "BIZTONSÁG ÉS ELLENŐRZÉS",
        cat_antialt: "ANTI-ALT RENDSZER",
        cat_mod: "MODERÁCIÓS MÁTRIX",
        cat_tickets: "TICKET NEXUS",
        cat_games: "JÁTÉK ARÉNA",
        cat_fun: "SZÓRAKOZÁS PROTOKOLLOK",
        cat_polls: "SZAVAZÁS RENDSZER",
        cat_roles: "SZEREPKÖR ÉPÍTÉSZ",
        cat_giveaway: "NYEREMÉNYJÁTÉK MOTOR",
        cat_nameauto: "NÉV AUTOMATIZÁLÁS",
        cat_ai: "AI NEURÁLIS LINK",
        cat_entertainment: "SZÓRAKOZTATÁSI RENDSZEREK",
        cat_engagement: "KÖZÖSSÉGI PROTOKOLLOK",
        cat_language: "RENDSZER KONFIGURÁCIÓ"
    }
};

// Language switching functionality
let currentLang = localStorage.getItem('language') || 'en';

function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Update toggle state
    const toggle = document.getElementById('langToggle');
    if (toggle) {
        toggle.checked = (lang === 'hu');
    }
}

// Initialize language on page load
document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLang);
    
    // Setup language toggle listener
    const toggle = document.getElementById('langToggle');
    if (toggle) {
        toggle.addEventListener('change', (e) => {
            setLanguage(e.target.checked ? 'hu' : 'en');
        });
    }
});

// CSS for toggle slider animation
const style = document.createElement('style');
style.textContent = `
    #langToggle:checked + span + span {
        transform: translateX(26px);
    }
`;
document.head.appendChild(style);
