// ── Category filter default ───────────────────────────────────────────────────
// List category names to pre-check on page load. [] = show all by default.
const DEFAULT_CATEGORIES = [];

$(document).ready(function() {
    setupWeightFilter();
    setupPlayerDropdown();
    loadBoardGames();
    setupFilters();
    loadUrlParameters();
    setupPrint();
});

// ── Weight circle toggle ──────────────────────────────────────────────────────

function setupWeightFilter() {
    $('.weight-btn').on('click', function() {
        $('.weight-btn').removeClass('active');
        $(this).addClass('active');
        applyFilters();
    });
}

function getSelectedWeights() {
    return $('.weight-btn.active[data-weight!="any"]')
        .map(function() { return parseInt($(this).data('weight')); })
        .get();
}

// ── Player count dropdown ─────────────────────────────────────────────────────

function setupPlayerDropdown() {
    $('#playerDropdownBtn').on('click', function(e) {
        e.stopPropagation();
        $('#playerDropdownMenu').toggleClass('open');
        $(this).toggleClass('open');
    });

    $(document).on('click.playerDropdown', function(e) {
        if (!$(e.target).closest('#playerDropdownWrap').length) {
            $('#playerDropdownMenu').removeClass('open');
            $('#playerDropdownBtn').removeClass('open');
        }
    });

    $(document).on('keydown.playerDropdown', function(e) {
        if (e.key === 'Escape') {
            $('#playerDropdownMenu').removeClass('open');
            $('#playerDropdownBtn').removeClass('open');
        }
    });

    $('.player-count-check').on('change', function() {
        updatePlayerDropdownLabel();
        applyFilters();
    });
}

function updatePlayerDropdownLabel() {
    const selected = $('.player-count-check:checked').map(function() { return this.value; }).get();
    $('#playerDropdownLabel').text(selected.length === 0 ? 'Any' : selected.join(', '));
}

function getSelectedPlayerCounts() {
    return $('.player-count-check:checked').map(function() { return this.value; }).get();
}

function matchesPlayerCountCheckboxes(selectedCounts, gamePlayerCount) {
    const gameCounts = parsePlayerCount(gamePlayerCount);
    return selectedCounts.some(function(sel) {
        if (sel === '8+') return gameCounts.some(function(n) { return n >= 8; });
        return gameCounts.includes(parseInt(sel));
    });
}

// ── Print ─────────────────────────────────────────────────────────────────────

function setupPrint() {
    window.addEventListener('beforeprint', createPrintTable);
}

function createPrintTable() {
    $('.print-table').remove();

    const visibleGames = [];
    $('.game-tile:visible').each(function() {
        visibleGames.push({
            image: $(this).find('img').attr('src') || '',
            name: $(this).data('name') || '',
            genre: $(this).data('genre') || '',
            players: $(this).data('player-count') || '',
            weight: $(this).data('weight') || '',
            description: $(this).data('description') || ''
        });
    });

    let tableHtml = `
        <table class="print-table">
            <thead>
                <tr>
                    <th class="col-image">Image</th>
                    <th class="col-name">Name</th>
                    <th class="col-genre">Genre</th>
                    <th class="col-players">Players</th>
                    <th class="col-weight">Weight</th>
                    <th class="col-description">Description</th>
                </tr>
            </thead>
            <tbody>
    `;

    visibleGames.forEach(game => {
        tableHtml += `
            <tr>
                <td class="col-image"><img src="${game.image}" alt="${game.name}"></td>
                <td class="col-name">${game.name}</td>
                <td class="col-genre">${game.genre}</td>
                <td class="col-players">${game.players}</td>
                <td class="col-weight">${game.weight}</td>
                <td class="col-description">${game.description}</td>
            </tr>
        `;
    });

    tableHtml += `</tbody></table>`;
    $('body').append(tableHtml);
}

// ── URL parameters ────────────────────────────────────────────────────────────

function loadUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const ids = urlParams.get('ids');
    if (ids) {
        $('#idFilter').val(ids);
        setTimeout(() => applyFilters(), 100);
    }
}

function updateUrlParameters() {
    const idFilter = $('#idFilter').val().trim();
    const url = new URL(window.location);
    if (idFilter) {
        url.searchParams.set('ids', idFilter);
    } else {
        url.searchParams.delete('ids');
    }
    window.history.pushState({}, '', url);
}

// ── Filters ───────────────────────────────────────────────────────────────────

function setupFilters() {
    $('#nameFilter, #genreFilter').on('input', applyFilters);
}

function applyFilters() {
    const nameFilter = $('#nameFilter').val().trim();
    const genreFilter = $('#genreFilter').val().trim();
    const idFilter = $('#idFilter').val().trim();
    const selectedWeights = getSelectedWeights();
    const selectedPlayerCounts = getSelectedPlayerCounts();

    $('.game-tile').each(function() {
        const tile = $(this);
        const gameData = {
            name: tile.data('name') || '',
            playerCount: tile.data('player-count') || '',
            genre: tile.data('genre') || '',
            weight: tile.data('weight') || '',
            id: tile.data('id') || '',
            description: tile.data('description') || '',
            notes: tile.data('notes') || ''
        };

        let show = true;

        if (nameFilter && !matchesTextFilter(nameFilter, gameData.name + ' ' + gameData.description + ' ' + gameData.notes)) {
            show = false;
        }
        if (genreFilter && !matchesTextFilter(genreFilter, gameData.genre)) {
            show = false;
        }
        if (idFilter && !matchesIdFilter(idFilter, gameData.id)) {
            show = false;
        }
        if (selectedWeights.length > 0 && !selectedWeights.includes(parseInt(gameData.weight))) {
            show = false;
        }
        if (selectedPlayerCounts.length > 0 && !matchesPlayerCountCheckboxes(selectedPlayerCounts, gameData.playerCount)) {
            show = false;
        }

        const checkedCategories = $('.category-checkbox:checked').map((_, el) => el.value).get();
        if (checkedCategories.length > 0) {
            const tileCategories = tile.data('categories') || [];
            if (!checkedCategories.some(cat => tileCategories.includes(cat))) {
                show = false;
            }
        }

        tile.toggle(show);
    });
}

function matchesTextFilter(filterValue, gameText) {
    const lowerFilter = filterValue.toLowerCase();
    const lowerGameText = gameText.toLowerCase();

    if (lowerFilter.includes('&')) {
        const andTerms = lowerFilter.split('&').map(term => term.trim());
        return andTerms.every(term => lowerGameText.includes(term));
    }
    if (lowerFilter.includes(',')) {
        const orTerms = lowerFilter.split(',').map(term => term.trim());
        return orTerms.some(term => lowerGameText.includes(term));
    }
    return lowerGameText.includes(lowerFilter);
}

function matchesIdFilter(filterValue, gameId) {
    const gameIdNum = parseInt(gameId);

    if (filterValue.includes('&')) {
        const andTerms = filterValue.split('&').map(term => parseInt(term.trim())).filter(num => !isNaN(num));
        return andTerms.every(term => term === gameIdNum);
    }
    if (filterValue.includes(',')) {
        const orTerms = filterValue.split(',').map(term => parseInt(term.trim())).filter(num => !isNaN(num));
        return orTerms.includes(gameIdNum);
    }

    const filterNum = parseInt(filterValue);
    return !isNaN(filterNum) && filterNum === gameIdNum;
}

function processNumericFilter(filterValue) {
    let numbers = [];
    const orTerms = filterValue.split(',').map(term => term.trim());

    orTerms.forEach(term => {
        if (term.includes('-')) {
            const [start, end] = term.split('-').map(num => parseInt(num.trim()));
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) numbers.push(i);
            }
        } else {
            const num = parseInt(term);
            if (!isNaN(num)) numbers.push(num);
        }
    });

    return [...new Set(numbers)];
}

function parsePlayerCount(playerCountString) {
    const str = playerCountString.toString().toLowerCase();
    let numbers = [];

    if (str.includes('-')) {
        const parts = str.split('-');
        if (parts.length === 2) {
            const start = parseInt(parts[0]);
            const end = parseInt(parts[1].replace(/[^\d]/g, ''));
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end; i++) numbers.push(i);
            }
        }
    } else if (str.includes('+')) {
        const baseNum = parseInt(str.replace('+', ''));
        if (!isNaN(baseNum)) {
            for (let i = baseNum; i <= 8; i++) numbers.push(i);
        }
    } else {
        const match = str.match(/\d+/);
        if (match) numbers.push(parseInt(match[0]));
    }

    return numbers;
}

// ── Data loading ──────────────────────────────────────────────────────────────

function loadBoardGames() {
    $.getJSON('https://raw.githubusercontent.com/TheRealFlyingPotato/TheRealFlyingPotato.github.io/refs/heads/master/board-game-catalog/boardgames.json')
        .done(function(data) {
            displayBoardGames(data);
        })
        .fail(function() {
            displayErrorMessage();
        });
}

function displayBoardGames(games) {
    const showHidden = new URLSearchParams(window.location.search).has('show_all');
    const container = $('.games-grid');
    container.empty();

    games.forEach(function(game) {
        if (game.hide === 1 && !showHidden) return;
        container.append(createGameTile(game));
    });

    buildCategoryCheckboxes(games);
}

function buildCategoryCheckboxes(games) {
    const allCategories = [...new Set(games.flatMap(g => g.category || []))].sort();

    if (allCategories.length === 0) {
        $('#categoryFilterSection').hide();
        return;
    }

    const container = $('#categoryFilter').empty();
    allCategories.forEach(function(cat) {
        const id = 'cat-' + cat.replace(/\s+/g, '-');
        const checked = DEFAULT_CATEGORIES.includes(cat) ? 'checked' : '';
        container.append(`
            <div class="form-check">
                <input class="form-check-input category-checkbox" type="checkbox"
                       id="${id}" value="${cat}" ${checked}>
                <label class="form-check-label" for="${id}">${cat}</label>
            </div>
        `);
    });

    $('.category-checkbox').on('change', applyFilters);

    if (DEFAULT_CATEGORIES.length > 0) {
        applyFilters();
    }
}

// ── Tile creation ─────────────────────────────────────────────────────────────

function createGameTile(game) {
    const tile = $('<div>', {
        class: 'game-tile',
        'data-id': game.id,
        'data-name': (game.name || '').toLowerCase(),
        'data-genre': (game.genre || '').toLowerCase(),
        'data-description': (game.description || '').toLowerCase(),
        'data-player-count': game['player count'] || '',
        'data-notes': (game.notes || '').toLowerCase(),
        'data-weight': game.weight || '',
        'data-categories': JSON.stringify(game.category || [])
    });

    // Image
    const img = $('<img>', {
        src: game.image,
        alt: game.name,
        loading: 'lazy'
    });

    // Overlay
    const overlay = $('<div>', { class: 'overlay' });

    const overlayTitle = $('<div>', {
        class: 'overlay-title',
        text: game.name
    });
    overlay.append(overlayTitle);

    if (game.description) {
        overlay.append($('<div>', {
            class: 'overlay-description',
            text: game.description
        }));
    }

    if (game.notes && game.notes.trim()) {
        overlay.append($('<div>', {
            class: 'overlay-notes',
            text: game.notes
        }));
    }

    tile.append(img, overlay);

    // Click → open BGG URL
    tile.on('click', function() {
        if (game.bggurl) {
            window.open(game.bggurl, '_blank');
        }
    });

    return tile;
}

function displayErrorMessage() {
    $('.games-grid').html(`
        <div style="grid-column: 1/-1; padding: 2rem; color: #fff;">
            <strong>Error loading games.</strong> Check that boardgames.json exists and is valid.
        </div>
    `);
}

window.boardGamesApp = {
    loadBoardGames: loadBoardGames
};
