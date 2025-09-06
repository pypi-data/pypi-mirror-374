import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { MessageHandler } from '../messageHandler';
import { environmentService } from './environmentService';

/**
 * Local settings - stored in JupyterLab registry only
 */
export interface ILocalSettings {
    serverUrl: string;
    username: string;
    usernameFromJupyterHub: boolean;
    bonnieUrl?: string;
    googleClientId?: string;
    _currentChatId?: string;
    toolsConfig?: string;
}

/**
 * Remote settings - stored on server only
 */
export interface IRemoteSettings {
    voittaApiKey: string;
    openaiApiKey: string;
    anthropicApiKey: string;
    geminiApiKey: string;
    maxMessages: number;
    proxyPort: number;
    primaryModel?: string;
    secondaryProvider?: string;
    imageParseProvider?: string;
}

/**
 * Complete settings interface for backward compatibility with existing code
 */
export interface IChatSettings extends ILocalSettings, IRemoteSettings { }

/**
 * Default local settings
 */
const DEFAULT_LOCAL_SETTINGS: ILocalSettings = {
    serverUrl: process.env.SERVER_URL || '/ws',
    username: 'User',
    usernameFromJupyterHub: false,
    bonnieUrl: 'ws://bonnie:8777/ws',
    googleClientId: ''
};

/**
 * Default remote settings
 */
const DEFAULT_REMOTE_SETTINGS: IRemoteSettings = {
    voittaApiKey: 'The Future Of Computing',
    openaiApiKey: '',
    anthropicApiKey: '',
    geminiApiKey: '',
    maxMessages: 100,
    proxyPort: 3000,
    primaryModel: undefined,
    secondaryProvider: undefined,
    imageParseProvider: undefined
};

/**
 * Settings Manager - handles clean separation between local and remote settings
 */
export class SettingsManager {
    private settingsRegistry: ISettingRegistry | null;
    private messageHandler: MessageHandler | null = null;
    private localSettings: ILocalSettings;
    private remoteSettings: IRemoteSettings;
    private onSettingsChanged?: (settings: IChatSettings) => void;

    constructor(settingsRegistry: ISettingRegistry | null) {
        this.settingsRegistry = settingsRegistry;
        this.localSettings = { ...DEFAULT_LOCAL_SETTINGS };
        this.remoteSettings = { ...DEFAULT_REMOTE_SETTINGS };
    }

    /**
     * Set the message handler for server communication
     */
    setMessageHandler(messageHandler: MessageHandler): void {
        this.messageHandler = messageHandler;
    }

    /**
     * Set callback for when settings change
     */
    setOnSettingsChanged(callback: (settings: IChatSettings) => void): void {
        this.onSettingsChanged = callback;
    }

    /**
     * Load local settings from JupyterLab registry
     */
    async loadLocalSettings(): Promise<ILocalSettings> {
        console.log('🔧 SETTINGS: Loading local settings from registry');

        if (!this.settingsRegistry) {
            console.warn('🔧 SETTINGS: Registry not available, using defaults');
            return { ...DEFAULT_LOCAL_SETTINGS };
        }

        try {
            const settings = await this.settingsRegistry.load('escobar:plugin');
            const composite = settings.composite as any;

            this.localSettings = {
                serverUrl: composite.serverUrl || DEFAULT_LOCAL_SETTINGS.serverUrl,
                username: composite.username || DEFAULT_LOCAL_SETTINGS.username,
                usernameFromJupyterHub: composite.usernameFromJupyterHub || DEFAULT_LOCAL_SETTINGS.usernameFromJupyterHub,
                bonnieUrl: composite.bonnieUrl || DEFAULT_LOCAL_SETTINGS.bonnieUrl,
                googleClientId: composite.googleClientId || DEFAULT_LOCAL_SETTINGS.googleClientId,
                _currentChatId: composite._currentChatId || '',
                toolsConfig: composite.toolsConfig || '{}'
            };

            // Always prioritize environment variable for serverUrl
            if (process.env.SERVER_URL) {
                this.localSettings.serverUrl = process.env.SERVER_URL;
                console.log('🔧 SETTINGS: Using serverUrl from environment');
            }

            console.log('🔧 SETTINGS: Local settings loaded successfully');
            return { ...this.localSettings };
        } catch (error) {
            console.error('🔧 SETTINGS: Failed to load local settings:', error);
            this.localSettings = { ...DEFAULT_LOCAL_SETTINGS };
            return { ...this.localSettings };
        }
    }

    /**
     * Save local settings to JupyterLab registry
     */
    async saveLocalSettings(settings: ILocalSettings): Promise<void> {
        console.log('🔧 SETTINGS: Saving local settings to registry');

        if (!this.settingsRegistry) {
            throw new Error('Settings registry not available');
        }

        try {
            const settingsPlugin = await this.settingsRegistry.load('escobar:plugin');

            console.log('📋 SCHEMA: Saving to registry:', {
                serverUrl: settings.serverUrl,
                username: settings.username,
                usernameFromJupyterHub: settings.usernameFromJupyterHub,
                bonnieUrl: settings.bonnieUrl,
                googleClientId: settings.googleClientId,
                _currentChatId: settings._currentChatId,
                toolsConfig: settings.toolsConfig
            });

            await settingsPlugin.set('serverUrl', settings.serverUrl);
            await settingsPlugin.set('username', settings.username);
            await settingsPlugin.set('usernameFromJupyterHub', settings.usernameFromJupyterHub);
            if (settings.bonnieUrl !== undefined) {
                await settingsPlugin.set('bonnieUrl', settings.bonnieUrl);
            }
            if (settings.googleClientId !== undefined) {
                await settingsPlugin.set('googleClientId', settings.googleClientId);
            }
            if (settings._currentChatId !== undefined) {
                await settingsPlugin.set('_currentChatId', settings._currentChatId);
            }
            if (settings.toolsConfig !== undefined) {
                await settingsPlugin.set('toolsConfig', settings.toolsConfig);
            }

            this.localSettings = { ...settings };
            console.log('🔧 SETTINGS: Local settings saved successfully');

            // Notify about settings change
            this.notifySettingsChanged();
        } catch (error) {
            console.error('📋 SCHEMA: Registry save failed:', error);
            throw error;
        }
    }

    /**
     * Load remote settings from server
     */
    async loadRemoteSettings(): Promise<IRemoteSettings> {
        console.log('🔧 SETTINGS: Loading remote settings from server');

        if (!this.messageHandler) {
            console.warn('🔧 SETTINGS: Message handler not available, using defaults');
            return { ...DEFAULT_REMOTE_SETTINGS };
        }

        try {
            console.log('📤 PROTOCOL: Sending retrieveSettings request');
            const serverSettings = await this.messageHandler.retrieveSettingsFromServer();
            console.log('📥 PROTOCOL: Received retrieveSettings response');

            this.remoteSettings = {
                voittaApiKey: serverSettings.voittaApiKey || DEFAULT_REMOTE_SETTINGS.voittaApiKey,
                openaiApiKey: serverSettings.openaiApiKey || DEFAULT_REMOTE_SETTINGS.openaiApiKey,
                anthropicApiKey: serverSettings.anthropicApiKey || DEFAULT_REMOTE_SETTINGS.anthropicApiKey,
                geminiApiKey: serverSettings.geminiApiKey || DEFAULT_REMOTE_SETTINGS.geminiApiKey,
                maxMessages: serverSettings.maxMessages || DEFAULT_REMOTE_SETTINGS.maxMessages,
                proxyPort: serverSettings.proxyPort || DEFAULT_REMOTE_SETTINGS.proxyPort,
                primaryModel: serverSettings.primaryModel,
                secondaryProvider: serverSettings.secondaryProvider,
                imageParseProvider: serverSettings.imageParseProvider
            };

            console.log('🔧 SETTINGS: Remote settings loaded successfully');
            return { ...this.remoteSettings };
        } catch (error) {
            console.warn('🔧 SETTINGS: Failed to load remote settings, using defaults:', error);
            this.remoteSettings = { ...DEFAULT_REMOTE_SETTINGS };
            return { ...this.remoteSettings };
        }
    }

    /**
     * Save remote settings to server
     */
    async saveRemoteSettings(settings: IRemoteSettings): Promise<void> {
        console.log('🔧 SETTINGS: Saving remote settings to server');

        if (!this.messageHandler) {
            throw new Error('Message handler not available for saving remote settings');
        }

        try {
            console.log('📤 PROTOCOL: Sending saveSettings request');
            await this.messageHandler.saveSettingsToServer(settings);
            console.log('📥 PROTOCOL: Received saveSettings response');

            this.remoteSettings = { ...settings };
            console.log('🔧 SETTINGS: Remote settings saved successfully');

            // Notify about settings change
            this.notifySettingsChanged();
        } catch (error) {
            console.error('🔧 SETTINGS: Failed to save remote settings:', error);
            throw error;
        }
    }

    /**
     * Get complete settings (combination of local and remote)
     */
    getCompleteSettings(): IChatSettings {
        return {
            ...this.localSettings,
            ...this.remoteSettings
        };
    }

    /**
     * Get only local settings
     */
    getLocalSettings(): ILocalSettings {
        return { ...this.localSettings };
    }

    /**
     * Get only remote settings
     */
    getRemoteSettings(): IRemoteSettings {
        return { ...this.remoteSettings };
    }

    /**
     * Auto-populate Google Client ID from environment variables if not set
     */
    async autoPopulateGoogleClientId(): Promise<void> {
        console.log('🔧 SETTINGS: Checking Google Client ID auto-population...');

        // Check if Google Client ID is already set in settings
        if (this.localSettings.googleClientId && this.localSettings.googleClientId.trim() !== '') {
            console.log('🔧 SETTINGS: Google Client ID already configured, skipping auto-population');
            return;
        }

        try {
            // Fetch Google Client ID from environment variables
            const envGoogleClientId = await environmentService.getGoogleClientId();

            if (envGoogleClientId && envGoogleClientId.trim() !== '') {
                console.log('🔧 SETTINGS: Found Google Client ID in environment variables');
                console.log('🔧 SETTINGS: Auto-populating Google Client ID from environment');

                // Update local settings with the environment variable value
                await this.updateLocalSetting('googleClientId', envGoogleClientId);

                console.log('🔧 SETTINGS: ✅ Successfully auto-populated Google Client ID from environment');
            } else {
                console.log('🔧 SETTINGS: No Google Client ID found in environment variables');
            }
        } catch (error) {
            console.warn('🔧 SETTINGS: Failed to auto-populate Google Client ID:', error);
            // Don't throw - this is a non-critical enhancement
        }
    }

    /**
     * Initialize settings - load both local and remote
     */
    async initializeSettings(): Promise<IChatSettings> {
        console.log('Initializing settings...');

        // Load local settings first
        await this.loadLocalSettings();

        // Auto-populate Google Client ID from environment if not set
        await this.autoPopulateGoogleClientId();

        // Try to load remote settings if message handler is available
        if (this.messageHandler) {
            try {
                await this.loadRemoteSettings();
            } catch (error) {
                console.warn('Could not load remote settings during initialization:', error);
            }
        }

        const completeSettings = this.getCompleteSettings();
        console.log('Settings initialization complete');
        return completeSettings;
    }

    /**
     * Update a specific local setting
     */
    async updateLocalSetting<K extends keyof ILocalSettings>(
        key: K,
        value: ILocalSettings[K]
    ): Promise<void> {
        const newLocalSettings = { ...this.localSettings, [key]: value };
        await this.saveLocalSettings(newLocalSettings);
    }

    /**
     * Update a specific remote setting
     */
    async updateRemoteSetting<K extends keyof IRemoteSettings>(
        key: K,
        value: IRemoteSettings[K]
    ): Promise<void> {
        const newRemoteSettings = { ...this.remoteSettings, [key]: value };
        await this.saveRemoteSettings(newRemoteSettings);
    }

    /**
     * Notify listeners about settings changes
     */
    private notifySettingsChanged(): void {
        if (this.onSettingsChanged) {
            this.onSettingsChanged(this.getCompleteSettings());
        }
    }

    /**
     * Listen for changes to local settings in the registry
     */
    setupLocalSettingsListener(): void {
        if (!this.settingsRegistry) {
            return;
        }

        this.settingsRegistry
            .load('escobar:plugin')
            .then(settings => {
                settings.changed.connect(() => {
                    // Reload local settings when registry changes
                    this.loadLocalSettings().then(() => {
                        this.notifySettingsChanged();
                    });
                });
            })
            .catch(error => {
                console.error('Failed to setup local settings listener:', error);
            });
    }
}
