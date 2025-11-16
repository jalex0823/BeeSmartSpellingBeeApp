/**
 * quiz-wordlist.js
 * Centralized Word List Manager for Quiz
 * 
 * Responsibilities:
 * - Persist currently active list (id, name, words, progress) in localStorage
 * - Compare server-provided selected_list to stored list on page load
 * - Override storage state when server provides a different list
 * - Provide public API: getCurrentWordList(), clearActiveWordList()
 * - Dispatch wordlist:changed event when list changes
 * - Update backward-compatible globals: window.QUIZ_WORDS, window.QUIZ_CURRENT_INDEX, window.QUIZ_ACTIVE_LIST_ID
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'beesmart_active_wordlist';
    const VERSION = '1.0';

    class WordListManager {
        constructor() {
            this.activeList = null;
            this.initialized = false;
            console.log('📋 WordListManager: Initializing...');
        }

        /**
         * Initialize the word list manager
         * Compares server-provided list to stored list and resolves conflicts
         */
        async init(serverProvidedList) {
            console.log('📋 WordListManager: init() called with:', serverProvidedList);
            
            const stored = this.loadFromStorage();
            console.log('📋 WordListManager: Loaded from storage:', stored);

            // If server provided a list, check if it differs from stored
            if (serverProvidedList && serverProvidedList.id) {
                const serverListId = String(serverProvidedList.id);
                const storedListId = stored ? String(stored.id) : null;

                if (serverListId !== storedListId) {
                    console.log(`📋 WordListManager: Server list (${serverListId}) differs from stored (${storedListId}) - overriding storage`);
                    await this.setActiveList(serverProvidedList);
                } else {
                    console.log(`📋 WordListManager: Server list (${serverListId}) matches stored - using server data to refresh`);
                    // Even if IDs match, refresh from server in case words changed
                    await this.setActiveList(serverProvidedList);
                }
            } else if (stored) {
                // No server list provided, use stored
                console.log('📋 WordListManager: No server list provided, using stored list');
                this.activeList = stored;
                this.notifyListChanged();
            } else {
                // No server list, no stored list
                console.log('📋 WordListManager: No server list and no stored list - empty state');
                this.activeList = null;
            }

            this.initialized = true;
            console.log('📋 WordListManager: Initialization complete. Active list:', this.activeList);
            return this.activeList;
        }

        /**
         * Set the active word list and persist to storage
         * @param {Object} listData - { id, name, words, wordsUrl }
         */
        async setActiveList(listData) {
            console.log('📋 WordListManager: setActiveList() called with:', listData);

            if (!listData) {
                console.warn('📋 WordListManager: setActiveList() called with null/undefined - clearing list');
                this.clearActiveList();
                return;
            }

            // Fetch words if wordsUrl provided but words array not provided
            let words = listData.words || [];
            if (!words.length && listData.wordsUrl) {
                console.log('📋 WordListManager: Fetching words from URL:', listData.wordsUrl);
                try {
                    const response = await fetch(listData.wordsUrl, {
                        credentials: 'same-origin',
                        cache: 'no-store'
                    });
                    const data = await response.json();
                    words = data.words || [];
                    console.log(`📋 WordListManager: Fetched ${words.length} words from URL`);
                } catch (error) {
                    console.error('📋 WordListManager: Error fetching words:', error);
                    words = [];
                }
            }

            // Parse words from data attribute if provided as string
            if (typeof words === 'string') {
                try {
                    words = JSON.parse(words);
                } catch (e) {
                    console.error('📋 WordListManager: Error parsing words JSON:', e);
                    words = [];
                }
            }

            this.activeList = {
                id: listData.id || 'default',
                name: listData.name || 'Word List',
                words: words,
                loadedAt: Date.now(),
                version: VERSION
            };

            this.saveToStorage();
            this.notifyListChanged();
            
            console.log(`📋 WordListManager: Active list set - ${this.activeList.name} (${this.activeList.words.length} words)`);
            return this.activeList;
        }

        /**
         * Clear the active word list from memory and storage
         */
        clearActiveList() {
            console.log('📋 WordListManager: Clearing active word list');
            this.activeList = null;
            localStorage.removeItem(STORAGE_KEY);
            this.notifyListChanged();
        }

        /**
         * Get the currently active word list
         */
        getCurrentWordList() {
            return this.activeList;
        }

        /**
         * Save current list to localStorage
         */
        saveToStorage() {
            if (!this.activeList) {
                localStorage.removeItem(STORAGE_KEY);
                return;
            }

            try {
                const data = JSON.stringify(this.activeList);
                localStorage.setItem(STORAGE_KEY, data);
                console.log('📋 WordListManager: Saved to localStorage');
            } catch (error) {
                console.error('📋 WordListManager: Error saving to localStorage:', error);
            }
        }

        /**
         * Load list from localStorage
         */
        loadFromStorage() {
            try {
                const data = localStorage.getItem(STORAGE_KEY);
                if (!data) return null;

                const list = JSON.parse(data);
                
                // Validate version
                if (list.version !== VERSION) {
                    console.log(`📋 WordListManager: Version mismatch (${list.version} vs ${VERSION}) - discarding stored data`);
                    localStorage.removeItem(STORAGE_KEY);
                    return null;
                }

                console.log(`📋 WordListManager: Loaded from storage - ${list.name} (${list.words?.length || 0} words)`);
                return list;
            } catch (error) {
                console.error('📋 WordListManager: Error loading from localStorage:', error);
                localStorage.removeItem(STORAGE_KEY);
                return null;
            }
        }

        /**
         * Notify listeners that the word list has changed
         * Updates backward-compatible global variables
         */
        notifyListChanged() {
            console.log('📋 WordListManager: Notifying list changed');

            // Update backward-compatible globals
            if (this.activeList) {
                window.QUIZ_WORDS = this.activeList.words || [];
                window.QUIZ_CURRENT_INDEX = 0;
                window.QUIZ_ACTIVE_LIST_ID = this.activeList.id;
                window.QUIZ_ACTIVE_LIST_NAME = this.activeList.name;
                console.log(`📋 WordListManager: Updated globals - QUIZ_WORDS: ${window.QUIZ_WORDS.length} words, ID: ${window.QUIZ_ACTIVE_LIST_ID}`);
            } else {
                window.QUIZ_WORDS = [];
                window.QUIZ_CURRENT_INDEX = 0;
                window.QUIZ_ACTIVE_LIST_ID = null;
                window.QUIZ_ACTIVE_LIST_NAME = null;
                console.log('📋 WordListManager: Cleared globals');
            }

            // Dispatch custom event
            const event = new CustomEvent('wordlist:changed', {
                detail: {
                    list: this.activeList,
                    words: window.QUIZ_WORDS,
                    listId: window.QUIZ_ACTIVE_LIST_ID,
                    listName: window.QUIZ_ACTIVE_LIST_NAME
                }
            });
            window.dispatchEvent(event);
            console.log('📋 WordListManager: Dispatched wordlist:changed event');
        }

        /**
         * Ensure using the selected list provided by server or stored
         * This is the main entry point called from quiz.html
         */
        async ensureUsingSelectedList(options = {}) {
            console.log('📋 WordListManager: ensureUsingSelectedList() called with:', options);
            
            const serverList = {
                id: options.selectedListId || options.id,
                name: options.selectedListName || options.name,
                words: options.words,
                wordsUrl: options.wordsUrl
            };

            // If server provided a list, use it
            if (serverList.id) {
                return await this.init(serverList);
            }

            // Otherwise, try to load from storage
            const stored = this.loadFromStorage();
            if (stored) {
                this.activeList = stored;
                this.notifyListChanged();
                return stored;
            }

            // No list available
            console.log('📋 WordListManager: No list available');
            return null;
        }
    }

    // Create global instance
    window.wordListManager = new WordListManager();

    // Public API functions for backward compatibility
    window.getCurrentWordList = function() {
        return window.wordListManager.getCurrentWordList();
    };

    window.clearActiveWordList = function() {
        window.wordListManager.clearActiveList();
    };

    // Wire up refresh button if present
    document.addEventListener('DOMContentLoaded', () => {
        const refreshBtn = document.getElementById('refreshWordListBtn') || 
                          document.querySelector('[data-action="refresh-word-list"]');
        
        if (refreshBtn) {
            console.log('📋 WordListManager: Wiring up refresh button');
            refreshBtn.addEventListener('click', () => {
                console.log('🔄 Refresh word list button clicked');
                
                // Confirm with user
                const confirmed = confirm('Are you sure you want to refresh the word list? This will clear the current active list and you will need to select a new one.');
                
                if (confirmed) {
                    window.clearActiveWordList();
                    alert('Word list cleared! Please select a new list to continue.');
                    // Optionally redirect to menu
                    // window.location.href = '/';
                }
            });
        } else {
            console.log('📋 WordListManager: No refresh button found in DOM');
        }
    });

    console.log('📋 WordListManager: Module loaded successfully');
})();
