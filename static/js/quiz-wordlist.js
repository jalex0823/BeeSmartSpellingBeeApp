/**
 * Quiz Word List Manager
 * 
 * Centralizes word list state management for the quiz page.
 * 
 * Current State (v1):
 * - Provides infrastructure for future word list selection features
 * - Tracks active word list in localStorage for potential future use
 * - Maintains backward-compatible globals for existing quiz code
 * - Provides refresh button handler to clear word list state
 * 
 * Future Enhancements:
 * - Server-side list selection tracking (pass list ID/name to template)
 * - Word list selector UI in quiz header
 * - Automatic detection of list changes across page reloads
 * - Override stale lists when server provides different list
 * 
 * The module is designed to work seamlessly with existing quiz code
 * and adds no breaking changes to the current workflow.
 */

(function() {
    'use strict';
    
    const STORAGE_KEY = 'beesmart_active_wordlist';
    
    /**
     * Word List Manager class
     */
    class QuizWordListManager {
        constructor() {
            this.currentList = null;
            this.initialized = false;
        }
        
        /**
         * Initialize the manager on page load
         * Compares server-provided list to stored list and overrides if different
         */
        init() {
            console.log('🎯 QuizWordListManager: Initializing...');
            
            // Get server-provided list metadata from DOM
            const anchor = document.getElementById('quiz-root');
            if (!anchor) {
                console.warn('⚠️ QuizWordListManager: No #quiz-root anchor found');
                return;
            }
            
            const selectedListId = anchor.dataset.selectedListId;
            const selectedListName = anchor.dataset.selectedListName;
            const wordsData = anchor.dataset.words;
            const wordsUrl = anchor.dataset.wordsUrl;
            
            console.log('📋 Server-provided list:', { selectedListId, selectedListName });
            
            // If we have a selected list from the server, use it
            if (selectedListId) {
                this.ensureUsingSelectedList({
                    selectedListId,
                    selectedListName,
                    words: wordsData ? this._parseWords(wordsData) : null,
                    wordsUrl
                });
            } else {
                // No server-provided list, check localStorage
                const stored = this._loadFromStorage();
                if (stored) {
                    console.log('📦 Using stored word list:', stored.listName);
                    this._activateList(stored);
                } else {
                    console.log('ℹ️ No word list available (server or stored)');
                }
            }
            
            // Set up refresh button
            this._setupRefreshButton();
            
            // Set up word list selector if present
            this._setupWordListSelector();
            
            this.initialized = true;
            console.log('✅ QuizWordListManager: Initialized');
        }
        
        /**
         * Ensure the quiz uses the selected list
         * Overrides any existing list if IDs differ
         */
        ensureUsingSelectedList({ selectedListId, selectedListName, words, wordsUrl }) {
            console.log('🔄 QuizWordListManager: Ensuring selected list is active:', selectedListId);
            
            const stored = this._loadFromStorage();
            
            // Check if the stored list matches the selected list
            if (stored && stored.listId === selectedListId) {
                console.log('✅ Stored list matches selected list, using it');
                this._activateList(stored);
                return;
            }
            
            // Different list or no stored list - override with server selection
            console.log('🔄 Server list differs from stored list, overriding...');
            
            if (words) {
                // Words provided directly
                this._setActiveList({
                    listId: selectedListId,
                    listName: selectedListName || 'Selected List',
                    words: words,
                    currentIndex: 0
                });
            } else if (wordsUrl) {
                // Fetch words from URL
                this._fetchAndSetList(selectedListId, selectedListName, wordsUrl);
            } else {
                console.warn('⚠️ No words or URL provided for selected list');
            }
        }
        
        /**
         * Get current word list
         */
        getCurrentWordList() {
            return this.currentList;
        }
        
        /**
         * Clear active word list from storage and memory
         */
        clearActiveWordList() {
            console.log('🗑️ QuizWordListManager: Clearing active word list');
            
            localStorage.removeItem(STORAGE_KEY);
            this.currentList = null;
            
            // Reset backward-compatible globals
            window.QUIZ_WORDS = [];
            window.QUIZ_CURRENT_INDEX = 0;
            window.QUIZ_ACTIVE_LIST_ID = null;
            
            // Emit event
            this._emitChange({
                listId: null,
                listName: null,
                words: [],
                currentIndex: 0
            });
            
            console.log('✅ Active word list cleared');
        }
        
        /**
         * Private: Parse words from JSON string
         */
        _parseWords(wordsData) {
            try {
                return JSON.parse(wordsData);
            } catch (e) {
                console.error('❌ Failed to parse words data:', e);
                return [];
            }
        }
        
        /**
         * Private: Load word list from localStorage
         */
        _loadFromStorage() {
            try {
                const data = localStorage.getItem(STORAGE_KEY);
                if (!data) return null;
                
                const stored = JSON.parse(data);
                console.log('📦 Loaded from storage:', stored.listName);
                return stored;
            } catch (e) {
                console.error('❌ Failed to load from storage:', e);
                return null;
            }
        }
        
        /**
         * Private: Save word list to localStorage
         */
        _saveToStorage(listData) {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(listData));
                console.log('💾 Saved to storage:', listData.listName);
            } catch (e) {
                console.error('❌ Failed to save to storage:', e);
            }
        }
        
        /**
         * Private: Set active list (in memory, storage, and globals)
         */
        _setActiveList(listData) {
            console.log('📝 Setting active list:', listData.listName);
            
            this.currentList = listData;
            this._saveToStorage(listData);
            this._updateGlobals(listData);
            this._emitChange(listData);
        }
        
        /**
         * Private: Activate a list (update globals and emit event)
         */
        _activateList(listData) {
            console.log('🎯 Activating list:', listData.listName);
            
            this.currentList = listData;
            this._updateGlobals(listData);
            this._emitChange(listData);
        }
        
        /**
         * Private: Update backward-compatible globals
         */
        _updateGlobals(listData) {
            window.QUIZ_WORDS = listData.words || [];
            window.QUIZ_CURRENT_INDEX = listData.currentIndex || 0;
            window.QUIZ_ACTIVE_LIST_ID = listData.listId;
            
            console.log('🌐 Updated globals:', {
                wordsCount: window.QUIZ_WORDS.length,
                currentIndex: window.QUIZ_CURRENT_INDEX,
                activeListId: window.QUIZ_ACTIVE_LIST_ID
            });
        }
        
        /**
         * Private: Emit wordlist:changed event
         */
        _emitChange(listData) {
            const event = new CustomEvent('wordlist:changed', {
                detail: {
                    listId: listData.listId,
                    listName: listData.listName,
                    words: listData.words || [],
                    currentIndex: listData.currentIndex || 0
                }
            });
            window.dispatchEvent(event);
            
            console.log('📢 Emitted wordlist:changed event');
        }
        
        /**
         * Private: Fetch words from URL and set as active list
         */
        async _fetchAndSetList(listId, listName, wordsUrl) {
            try {
                console.log('🌐 Fetching words from:', wordsUrl);
                
                // Replace {id} placeholder in URL template if present
                const url = wordsUrl.includes('{id}') ? wordsUrl.replace('{id}', listId) : wordsUrl;
                
                const response = await fetch(url, {
                    credentials: 'same-origin',
                    cache: 'no-store',
                    headers: {
                        'Cache-Control': 'no-cache'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                const words = data.words || [];
                
                console.log(`✅ Fetched ${words.length} words`);
                
                this._setActiveList({
                    listId,
                    listName,
                    words,
                    currentIndex: 0
                });
            } catch (e) {
                console.error('❌ Failed to fetch words:', e);
                // Show user-friendly error if BeeSmart is available
                if (window.BeeSmart && window.BeeSmart.showError) {
                    window.BeeSmart.showError('Failed to load word list');
                }
            }
        }
        
        /**
         * Private: Set up refresh button
         */
        _setupRefreshButton() {
            const refreshBtn = document.getElementById('refreshWordListBtn') || 
                              document.querySelector('[data-action="refresh-word-list"]');
            
            if (!refreshBtn) {
                console.log('ℹ️ No refresh button found');
                return;
            }
            
            console.log('🔄 Setting up refresh button');
            
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                
                console.log('🔄 Refresh button clicked');
                
                // Clear the active list
                this.clearActiveWordList();
                
                // Show confirmation if BeeSmart is available
                if (window.BeeSmart && window.BeeSmart.showSuccess) {
                    window.BeeSmart.showSuccess('Word list cleared! Select a new list to continue.');
                }
                
                // Optionally redirect to menu or reload
                // For now, just clear - the user can select a new list
            });
        }
        
        /**
         * Private: Set up word list selector (if present)
         */
        _setupWordListSelector() {
            const selector = document.getElementById('wordListSelect');
            
            if (!selector) {
                console.log('ℹ️ No word list selector found');
                return;
            }
            
            console.log('📋 Setting up word list selector');
            
            selector.addEventListener('change', (e) => {
                const selectedId = e.target.value;
                const selectedOption = e.target.options[e.target.selectedIndex];
                const selectedName = selectedOption.text;
                
                if (!selectedId) {
                    console.log('ℹ️ No list selected');
                    return;
                }
                
                console.log('📋 List selected:', { selectedId, selectedName });
                
                // Get words URL template from selector
                const wordsUrlTemplate = selector.dataset.wordsUrlTemplate || '/api/lists/{id}/words';
                
                // Get words directly from option if available
                const wordsData = selectedOption.dataset.words;
                
                // Override current list with the newly selected one
                this.ensureUsingSelectedList({
                    selectedListId: selectedId,
                    selectedListName: selectedName,
                    words: wordsData ? this._parseWords(wordsData) : null,
                    wordsUrl: wordsUrlTemplate
                });
            });
        }
    }
    
    // Initialize manager when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.quizWordListManager = new QuizWordListManager();
            window.quizWordListManager.init();
            
            // Listen for quiz initialization to sync state
            _syncWithQuizManager();
        });
    } else {
        window.quizWordListManager = new QuizWordListManager();
        window.quizWordListManager.init();
        
        // Listen for quiz initialization to sync state
        _syncWithQuizManager();
    }
    
    /**
     * Private: Sync with existing quiz manager when it initializes
     */
    function _syncWithQuizManager() {
        // When the quiz manager is initialized, sync the word list state
        const checkQuizManager = setInterval(() => {
            if (window.quizManager) {
                clearInterval(checkQuizManager);
                
                // If we have a stored list, make sure it's available to the quiz
                const manager = window.quizWordListManager;
                if (manager && manager.currentList) {
                    console.log('📊 Syncing word list with quiz manager');
                    
                    // Update globals to ensure quiz has access to the list
                    window.QUIZ_WORDS = manager.currentList.words || [];
                    window.QUIZ_CURRENT_INDEX = manager.currentList.currentIndex || 0;
                    window.QUIZ_ACTIVE_LIST_ID = manager.currentList.listId;
                    
                    console.log('✅ Word list synced with quiz manager');
                }
            }
        }, 100); // Check every 100ms
        
        // Stop checking after 10 seconds
        setTimeout(() => clearInterval(checkQuizManager), 10000);
    }
    
    // Export helper functions for backward compatibility
    window.getCurrentWordList = function() {
        return window.quizWordListManager ? window.quizWordListManager.getCurrentWordList() : null;
    };
    
    window.clearActiveWordList = function() {
        if (window.quizWordListManager) {
            window.quizWordListManager.clearActiveWordList();
        }
    };
    
    console.log('📦 Quiz Word List Manager module loaded');
})();
