import { DocEvents } from 'yjs/dist/src/internals';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { createSettingsPage, showConnectionSettings } from './setting_page';
import { IFrame } from '@jupyterlab/ui-components';
import { memoryBank } from '../integrations/jupyter_integrations';
import { initializeGoogleAuth, getGoogleAuthManager, IGoogleAuthResult } from '../utils/googleAuth';
import { showToolsSelection, IToolInfo } from './tools_selection_page';

/**
 * Get SVG icon for AI provider
 * @param provider The AI provider name
 * @returns SVG string for the provider icon
 */
export function getProviderIcon(provider: string): string {
  const normalizedProvider = provider?.toLowerCase() || '';

  switch (normalizedProvider) {
    case 'openai':
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z" fill="#10A37F"/>
      </svg>`;

    case 'anthropic':
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L3 22h4.5l1.5-4h6l1.5 4H21L12 2zm-2.5 12l2.5-6.5L14.5 14h-5z" fill="#D97706"/>
      </svg>`;

    case 'gemini':
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2l3.09 6.26L22 9l-5.91 3.74L17.18 22 12 18.27 6.82 22l1.09-9.26L2 9l6.91-.74L12 2z" fill="#4285F4"/>
      </svg>`;

    default:
      // Generic AI icon for unknown providers
      return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#666"/>
      </svg>`;
  }
}

/**
 * Get provider display name
 * @param provider The AI provider name
 * @returns Formatted display name
 */
export function getProviderDisplayName(provider: string): string {
  const normalizedProvider = provider?.toLowerCase() || '';

  switch (normalizedProvider) {
    case 'openai':
      return 'OpenAI';
    case 'anthropic':
      return 'Anthropic';
    case 'gemini':
      return 'Gemini';
    default:
      return provider || 'Unknown';
  }
}

/**
 * Create an icon button with tooltip
 * @param className CSS class for the button
 * @param style CSS style string for the button
 * @param svgContent Inline SVG content
 * @param tooltip Tooltip text for mouseover
 * @returns The created button element
 */
export function createIconButton(className: string, style: string, svgContent: string, tooltip: string): HTMLButtonElement {
  const button = document.createElement('button');
  button.className = `escobar-icon-button ${className}`;
  button.title = tooltip; // This adds the native tooltip on hover
  button.style.cssText = style; // Apply the custom style

  // Create a span to hold the SVG content
  const iconSpan = document.createElement('span');
  iconSpan.className = 'escobar-icon-container';
  iconSpan.innerHTML = svgContent;

  button.appendChild(iconSpan);
  return button;
}

/**
 * Create a chat selection dropdown interface
 * @param onChatSelect Callback when a chat is selected
 * @param onNewChat Callback for creating a new chat
 * @param onRefreshChats Callback to refresh the chat list
 * @returns The chat selection container element
 */
export function createChatSelectionInterface(
  onChatSelect: (chatId: string) => Promise<void>,
  onNewChat: (provider?: string) => Promise<void>,
  onRefreshChats: () => Promise<any[]>
): HTMLDivElement {
  const container = document.createElement('div');
  container.className = 'escobar-chat-selection-container';
  container.style.cssText = `
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    border-bottom: 1px solid var(--jp-border-color1);
    background: var(--jp-layout-color0);
  `;

  // Chat selection dropdown
  const chatSelect = document.createElement('select');
  chatSelect.className = 'escobar-chat-select';
  chatSelect.style.cssText = `
    flex: 1;
    padding: 6px 8px;
    background: var(--jp-layout-color1);
    color: var(--jp-content-font-color1);
    border: 1px solid var(--jp-border-color1);
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
  `;

  // Add default option
  const defaultOption = document.createElement('option');
  defaultOption.value = '';
  defaultOption.textContent = 'Select a chat...';
  defaultOption.disabled = true;
  defaultOption.selected = true;
  chatSelect.appendChild(defaultOption);

  // Handle chat selection
  chatSelect.addEventListener('change', async () => {
    const selectedChatId = chatSelect.value;
    if (selectedChatId) {
      await onChatSelect(selectedChatId);
    }
  });

  // New chat button with model selection
  const newChatButton = document.createElement('button');
  newChatButton.className = 'escobar-new-chat-button';
  newChatButton.textContent = 'New Chat';
  newChatButton.style.cssText = `
    padding: 6px 12px;
    background: var(--jp-brand-color1);
    color: var(--jp-ui-inverse-font-color1);
    border: none;
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    white-space: nowrap;
  `;

  // Model selection dropdown (initially hidden)
  const modelSelect = document.createElement('select');
  modelSelect.className = 'escobar-model-select';
  modelSelect.style.cssText = `
    padding: 6px 8px;
    background: var(--jp-layout-color1);
    color: var(--jp-content-font-color1);
    border: 1px solid var(--jp-border-color1);
    border-radius: 4px;
    font-size: 13px;
    cursor: pointer;
    display: none;
  `;

  // Add model options
  const models = [
    { value: '', text: 'Select Model...' },
    { value: 'openai', text: 'OpenAI' },
    { value: 'anthropic', text: 'Anthropic' },
    { value: 'gemini', text: 'Gemini' }
  ];

  models.forEach(model => {
    const option = document.createElement('option');
    option.value = model.value;
    option.textContent = model.text;
    if (model.value === '') {
      option.disabled = true;
      option.selected = true;
    }
    modelSelect.appendChild(option);
  });

  // Show model selection when new chat is clicked
  newChatButton.addEventListener('click', () => {
    if (modelSelect.style.display === 'none') {
      modelSelect.style.display = 'inline-block';
      newChatButton.textContent = 'Cancel';
    } else {
      modelSelect.style.display = 'none';
      newChatButton.textContent = 'New Chat';
      modelSelect.value = '';
    }
  });

  // Handle model selection
  modelSelect.addEventListener('change', async () => {
    const selectedModel = modelSelect.value;
    if (selectedModel) {
      await onNewChat(selectedModel);
      modelSelect.style.display = 'none';
      newChatButton.textContent = 'New Chat';
      modelSelect.value = '';
      // Refresh chat list after creating new chat
      await refreshChatList();
    }
  });

  // Refresh button
  const refreshButton = document.createElement('button');
  refreshButton.className = 'escobar-refresh-button';
  refreshButton.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path>
    </svg>
  `;
  refreshButton.title = 'Refresh chat list';
  refreshButton.style.cssText = `
    padding: 6px;
    background: transparent;
    color: var(--jp-content-font-color1);
    border: 1px solid var(--jp-border-color1);
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  // Function to refresh chat list
  const refreshChatList = async () => {
    try {
      const chats = await onRefreshChats();

      // Clear existing options except the default
      while (chatSelect.children.length > 1) {
        chatSelect.removeChild(chatSelect.lastChild!);
      }

      // Add chat options
      chats.forEach(chat => {
        const option = document.createElement('option');
        option.value = chat.chatId;
        option.textContent = `${chat.title || 'Untitled'} (${chat.model || 'Unknown'}) - ${chat.lastModified || 'Unknown'}`;
        chatSelect.appendChild(option);
      });
    } catch (error) {
      console.error('Error refreshing chat list:', error);
    }
  };

  refreshButton.addEventListener('click', refreshChatList);

  // Initial load of chats
  refreshChatList();

  container.appendChild(chatSelect);
  container.appendChild(modelSelect);
  container.appendChild(newChatButton);
  container.appendChild(refreshButton);

  // Expose refresh function for external use
  (container as any).refreshChatList = refreshChatList;

  return container;
}

/**
 * Create the top buttons for the chat interface
 * @param app JupyterFrontEnd instance
 * @param settingsRegistry Settings registry
 * @param getSettings Function to get the current settings
 * @param onNewChat Callback for new chat button
 * @param onReconnect Callback for reconnect button
 * @param onSettingsUpdate Callback for when settings are updated
 * @param availableChats Array of available chats
 * @param onChatSelect Callback for when a chat is selected
 * @param currentChatId Current active chat ID
 * @param availableModels Array of available models from server
 * @returns The button container element
 */
export function createTopButtons(
  app: JupyterFrontEnd,
  settingsRegistry: ISettingRegistry | null,
  getSettings: () => any,
  onNewChat: (provider?: string) => Promise<void>,
  onReconnect: () => Promise<void>,
  onSettingsUpdate: (newSettings: any) => void,
  availableChats: any[] = [],
  onChatSelect?: (chatId: string) => Promise<void>,
  currentChatId: string = 'temp-session',
  availableModels: Array<{ model: string, provider: string }> = []
): HTMLDivElement {
  // Create button container for top buttons
  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'escobar-button-container';
  buttonContainer.style.position = 'relative'; // For warning positioning

  // Style for all icon buttons to ensure consistent appearance
  const buttonStyle = `
    font-weight: bold;
    margin: 0 5px;
    padding: 5px;
    background: transparent;
    border: none;
    color: var(--jp-content-font-color1);
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s ease;
  `;

  // Model dropdown removed - now handled in settings page

  // Create New Chat button with plus icon
  const newChatButton = createIconButton(
    'escobar-new-chat-button',
    buttonStyle,
    `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
      <line x1="12" y1="5" x2="12" y2="19"></line>
      <line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>`,
    'New Chat'
  );

  // Create warning message container (initially hidden)
  const warningContainer = document.createElement('div');
  warningContainer.className = 'escobar-warning-container';
  warningContainer.style.cssText = `
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--jp-warn-color0);
    color: var(--jp-warn-color1);
    border: 1px solid var(--jp-warn-color1);
    border-radius: 4px;
    padding: 8px;
    font-size: 12px;
    z-index: 1000;
    display: none;
    margin-top: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  `;

  // Track if we're in an existing chat (not temp-session)
  let isInExistingChat = false;

  // Function to update chat state
  const updateChatState = (chatId: string) => {
    isInExistingChat = chatId !== 'temp-session' && chatId !== '';
  };

  // Expose function to update chat state from outside
  (buttonContainer as any).updateChatState = updateChatState;

  // Handle new chat button click
  newChatButton.addEventListener('click', async () => {
    // Hide any visible warning
    warningContainer.style.display = 'none';

    // Create new chat (model selection now handled in settings)
    await onNewChat();
    console.log('New chat created');

    // Update chat state to indicate we're now in a new chat
    isInExistingChat = true;
  });

  // Click outside to hide warning
  document.addEventListener('click', (e) => {
    if (!warningContainer.contains(e.target as Node)) {
      warningContainer.style.display = 'none';
    }
  });

  // Add elements directly to button container (streamlined layout)
  buttonContainer.appendChild(newChatButton);
  buttonContainer.appendChild(warningContainer);

  // Create reconnect button with inline SVG
  const reconnectButton = createIconButton(
    'escobar-reconnect-button',
    buttonStyle,
    `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
      <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"></path>
    </svg>`,
    'Reconnect'
  );
  reconnectButton.addEventListener('click', async () => {
    console.log('Reconnect button clicked');

    try {
      // Call the reconnect function
      await onReconnect();
      console.log('Reconnected and initialized successfully');

      // Blink the reconnect icon 3 times to indicate success
      const iconContainer = reconnectButton.querySelector('.escobar-icon-container') as HTMLElement;
      if (iconContainer) {
        // Store original opacity
        const originalOpacity = iconContainer.style.opacity || '1';

        // Blink 3 times (fade out and in)
        for (let i = 0; i < 3; i++) {
          // Fade out
          iconContainer.style.opacity = '0.2';
          await new Promise(resolve => setTimeout(resolve, 150));

          // Fade in
          iconContainer.style.opacity = '1';
          await new Promise(resolve => setTimeout(resolve, 150));
        }
      }
    } catch (e) {
      console.error('Error reconnecting to server:', e);
      // Error handling is done in the callback
    }
  });
  buttonContainer.appendChild(reconnectButton);

  // Create UI button with inline SVG (crossed hammers icon)
  const uiButton = createIconButton(
    'escobar-ui-button',
    buttonStyle,
    `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
      <!-- First hammer head (top-left) -->
      <rect x="3" y="3" width="6" height="3" rx="1" fill="currentColor" stroke="none" transform="rotate(45 6 4.5)"/>
      <!-- First hammer handle (diagonal from head to bottom-right) -->
      <line x1="7" y1="7" x2="17" y2="17" stroke-width="2.5" stroke-linecap="round"/>
      
      <!-- Second hammer head (top-right) -->
      <rect x="15" y="3" width="6" height="3" rx="1" fill="currentColor" stroke="none" transform="rotate(-45 18 4.5)"/>
      <!-- Second hammer handle (diagonal from head to bottom-left) -->
      <line x1="17" y1="7" x2="7" y2="17" stroke-width="2.5" stroke-linecap="round"/>
      
      <!-- Center crossing point reinforcement -->
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/>
    </svg>`,
    'Tools Selection'
  );
  uiButton.addEventListener('click', () => {
    // Get available tools from global storage
    const availableTools = (window as any).escobarAvailableTools as IToolInfo[] || [];

    // Parse tools configuration from settings (default to all enabled)
    const currentSettings = getSettings();
    const toolsConfigStr = currentSettings.toolsConfig || '{}';

    let toolsConfig;
    try {
      toolsConfig = JSON.parse(toolsConfigStr);
    } catch (error) {
      toolsConfig = {};
    }

    const endpoints = toolsConfig.endpoints || {};

    // Default to enabled (true) unless explicitly disabled (false)
    const enabledTools = availableTools.filter(tool =>
      endpoints[tool.name] !== false
    ).map(tool => tool.name);

    showToolsSelection(
      availableTools,
      enabledTools,
      (selectedTools: string[]) => {
        // Convert selected tools to JSON format
        const newEndpoints = {};
        availableTools.forEach(tool => {
          newEndpoints[tool.name] = selectedTools.includes(tool.name);
        });

        const newToolsConfig = JSON.stringify({ endpoints: newEndpoints });

        // Save the tools configuration to settings
        if (settingsRegistry) {
          settingsRegistry.load('escobar:plugin').then(settings => {
            settings.set('toolsConfig', newToolsConfig);
          }).catch(error => {
            console.error('Failed to save tools configuration:', error);
          });
        }

        // Update global settings
        const updatedSettings = { ...currentSettings, toolsConfig: newToolsConfig };
        (window as any).escobarCurrentSettings = updatedSettings;

        // Call settings update callback
        onSettingsUpdate(updatedSettings);
      }
    );
  });
  buttonContainer.appendChild(uiButton);

  // Create chat dropdown (between UI and Settings)
  const chatDropdown = document.createElement('select');
  chatDropdown.className = 'escobar-chat-dropdown';
  chatDropdown.style.cssText = `
    font-weight: bold;
    margin: 0 5px;
    padding: 5px 8px;
    background: var(--jp-layout-color0);
    color: var(--jp-content-font-color1);
    border: 1px solid var(--jp-border-color1);
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    min-width: 150px;
    max-width: 200px;
  `;

  // Function to update chat dropdown
  const updateChatDropdown = (newChats?: any[], newCurrentChatId?: string) => {
    // Update the available chats if provided
    if (newChats !== undefined) {
      availableChats.length = 0; // Clear existing array
      availableChats.push(...newChats); // Add new chats
    }

    // Update current chat ID if provided
    if (newCurrentChatId !== undefined) {
      currentChatId = newCurrentChatId;
    }

    // Clear existing options
    chatDropdown.innerHTML = '';

    // Add available chats (filtered to exclude temp-session)
    const filteredChats = availableChats.filter(chat =>
      chat.chatId && chat.chatId !== 'temp-session'
    );

    // Only add real chats to dropdown
    filteredChats.forEach(chat => {
      const option = document.createElement('option');
      option.value = chat.chatId;

      // Simplified: only chat name and date/time
      const chatTitle = chat.title || 'Untitled Chat';

      // Parse and format date with time
      let formattedDateTime = 'Unknown';
      if (chat.lastModified && chat.lastModified !== 'Unknown') {
        try {
          const date = new Date(chat.lastModified);

          // Check if date is valid
          if (!isNaN(date.getTime())) {
            // Format to show date and time: "6/28/2025, 2:28 PM"
            formattedDateTime = date.toLocaleString('en-US', {
              month: 'numeric',
              day: 'numeric',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              hour12: true
            });
          }
        } catch (error) {
          console.warn('Error parsing date:', chat.lastModified, error);
        }
      }

      option.textContent = `${chatTitle} - ${formattedDateTime}`;
      chatDropdown.appendChild(option);
    });

    // Always show the dropdown
    chatDropdown.style.display = 'inline-block';

    // Set current selection only if it's not temp-session and the chat exists in dropdown
    if (currentChatId !== 'temp-session' && filteredChats.length > 0) {
      const chatExists = filteredChats.some(chat => chat.chatId === currentChatId);
      if (chatExists) {
        chatDropdown.value = currentChatId;
      }
    }
  };

  // Handle chat selection
  chatDropdown.addEventListener('change', async () => {
    const selectedChatId = chatDropdown.value;
    if (selectedChatId && onChatSelect) {
      console.log('Chat dropdown selection:', selectedChatId);
      await onChatSelect(selectedChatId);
    }
  });

  // Initial population of dropdown
  updateChatDropdown();

  // Expose function to update dropdown from outside
  (buttonContainer as any).updateChatDropdown = updateChatDropdown;

  buttonContainer.appendChild(chatDropdown);

  // Create Google Auth button with key icon
  const googleAuthButton = createIconButton(
    'escobar-google-auth-button',
    buttonStyle,
    `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
      <circle cx="12" cy="7" r="4"/>
      <path d="M12 11v10"/>
      <path d="M14 19h4"/>
      <path d="M14 16h3"/>
      <path d="M14 22h2"/>
    </svg>`,
    'Google Authentication'
  );

  // Handle Google Auth button click
  googleAuthButton.addEventListener('click', async () => {
    console.log('🔐 UI: Google Auth button clicked');

    try {
      // Get current settings to check for Google Client ID
      const currentSettings = getSettings();
      const googleClientId = currentSettings.googleClientId;

      if (!googleClientId) {
        // Show error message if no client ID is configured
        const errorMessage = document.createElement('div');
        errorMessage.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          background: var(--jp-error-color0);
          color: var(--jp-error-color1);
          padding: 12px 16px;
          border-radius: 4px;
          border: 1px solid var(--jp-error-color1);
          z-index: 10000;
          font-size: 14px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        errorMessage.textContent = 'Google Client ID not configured. Please set it in the settings first.';
        document.body.appendChild(errorMessage);

        // Remove error message after 5 seconds
        setTimeout(() => {
          if (errorMessage.parentNode) {
            errorMessage.parentNode.removeChild(errorMessage);
          }
        }, 5000);
        return;
      }

      // Initialize Google Auth if not already done
      let authManager = getGoogleAuthManager();
      if (!authManager) {
        authManager = initializeGoogleAuth({
          clientId: googleClientId,
          scope: 'openid email profile https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly'
        });
      }

      // Show loading state
      const originalContent = googleAuthButton.innerHTML;
      googleAuthButton.innerHTML = `
        <span class="escobar-icon-container">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
            <path d="M21 12a9 9 0 11-6.219-8.56"/>
          </svg>
        </span>
      `;
      googleAuthButton.disabled = true;

      // Attempt login using OAuth authorization code flow
      const result: IGoogleAuthResult = await authManager.loginWithAuthCode();

      // Restore button state
      googleAuthButton.innerHTML = originalContent;
      googleAuthButton.disabled = false;

      if (result.success && result.authorizationCode) {
        console.log('🔐 UI: Google OAuth successful, received authorization code');
        console.log('🔐 UI: Auth code:', result.authorizationCode.substring(0, 20) + '...');

        // Import updateCredentials function
        const { updateCredentials } = await import('../utils/googleAuth');

        // Call updateCredentials with the authorization code
        const updateResult = await updateCredentials(
          result.authorizationCode,
          result.redirectUri || authManager.getRedirectUri(),
          googleClientId,
          undefined, // client secret (optional for public clients)
          result.state
        );

        if (updateResult.success) {
          console.log('🔐 UI: Credentials updated successfully');
          console.log('🔐 UI: User:', updateResult.userInfo?.email);

          // Store user info globally for backend communication
          (window as any).escobarGoogleUserInfo = updateResult.userInfo;

          console.log('🔐 UI: User info stored globally');

          // Update button tooltip to show authenticated state
          googleAuthButton.title = `Authenticated as ${updateResult.userInfo?.email || 'Google User'}`;

          // Show success message
          const successMessage = document.createElement('div');
          successMessage.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--jp-success-color0);
            color: var(--jp-success-color1);
            padding: 12px 16px;
            border-radius: 4px;
            border: 1px solid var(--jp-success-color1);
            z-index: 10000;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          `;
          successMessage.textContent = `Successfully authenticated as ${updateResult.userInfo?.email || 'Google User'}`;
          document.body.appendChild(successMessage);

          // Remove success message after 3 seconds
          setTimeout(() => {
            if (successMessage.parentNode) {
              successMessage.parentNode.removeChild(successMessage);
            }
          }, 3000);

        } else {
          console.error('🔐 UI: Failed to update credentials:', updateResult.error);

          // Show error message
          const errorMessage = document.createElement('div');
          errorMessage.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--jp-error-color0);
            color: var(--jp-error-color1);
            padding: 12px 16px;
            border-radius: 4px;
            border: 1px solid var(--jp-error-color1);
            z-index: 10000;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
          `;
          errorMessage.textContent = `Credential update failed: ${updateResult.error || 'Unknown error'}`;
          document.body.appendChild(errorMessage);

          // Remove error message after 5 seconds
          setTimeout(() => {
            if (errorMessage.parentNode) {
              errorMessage.parentNode.removeChild(errorMessage);
            }
          }, 5000);
        }

      } else {
        console.error('🔐 UI: Google authentication failed:', result.error);

        // Show error message
        const errorMessage = document.createElement('div');
        errorMessage.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          background: var(--jp-error-color0);
          color: var(--jp-error-color1);
          padding: 12px 16px;
          border-radius: 4px;
          border: 1px solid var(--jp-error-color1);
          z-index: 10000;
          font-size: 14px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        errorMessage.textContent = `Authentication failed: ${result.error || 'Unknown error'}`;
        document.body.appendChild(errorMessage);

        // Remove error message after 5 seconds
        setTimeout(() => {
          if (errorMessage.parentNode) {
            errorMessage.parentNode.removeChild(errorMessage);
          }
        }, 5000);
      }

    } catch (error) {
      console.error('🔐 UI: Error during Google authentication:', error);

      // Restore button state
      const originalContent = `
        <span class="escobar-icon-container">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
            <circle cx="12" cy="7" r="4"/>
            <path d="M12 11v10"/>
            <path d="M14 19h4"/>
            <path d="M14 16h3"/>
            <path d="M14 22h2"/>
          </svg>
        </span>
      `;
      googleAuthButton.innerHTML = originalContent;
      googleAuthButton.disabled = false;

      // Show error message
      const errorMessage = document.createElement('div');
      errorMessage.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--jp-error-color0);
        color: var(--jp-error-color1);
        padding: 12px 16px;
        border-radius: 4px;
        border: 1px solid var(--jp-error-color1);
        z-index: 10000;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      `;
      errorMessage.textContent = `Authentication error: ${error.message || 'Unknown error occurred'}`;
      document.body.appendChild(errorMessage);

      // Remove error message after 5 seconds
      setTimeout(() => {
        if (errorMessage.parentNode) {
          errorMessage.parentNode.removeChild(errorMessage);
        }
      }, 5000);
    }
  });

  buttonContainer.appendChild(googleAuthButton);

  // Create settings button with inline SVG
  const settingsButton = createIconButton(
    'escobar-settings-button',
    buttonStyle,
    `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
    </svg>`,
    'Settings'
  );
  settingsButton.addEventListener('click', () => {
    // Create and show settings page
    if (settingsRegistry) {
      // Always use the most up-to-date settings
      const settingsPage = createSettingsPage(
        settingsRegistry,
        getSettings(), // Get the current settings
        (newSettings) => {
          // Update settings when saved
          onSettingsUpdate(newSettings);
          console.log('Settings updated:', newSettings);
        }
      );
      settingsPage.show();
    } else {
      console.error('Settings registry not available');
    }
  });
  buttonContainer.appendChild(settingsButton);

  // Create connection button with inline SVG (lightning bolt icon)
  const connectionButton = createIconButton(
    'escobar-connection-button',
    buttonStyle,
    `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="escobar-icon-svg">
      <polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2"></polygon>
    </svg>`,
    'Connection Settings'
  );
  connectionButton.addEventListener('click', () => {
    // Create and show connection settings page
    if (settingsRegistry) {
      // Create a simple connection settings modal
      showConnectionSettings(settingsRegistry, getSettings(), onSettingsUpdate);
    } else {
      console.error('Settings registry not available');
    }
  });
  buttonContainer.appendChild(connectionButton);

  return buttonContainer;
}
