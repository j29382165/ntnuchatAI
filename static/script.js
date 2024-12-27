$(document).ready(function () {
  const chatInput = $('.chat-input textarea');
  const sendButton = $('.chat-input button');
  const chatContent = $('.chat-content');
  const placeholder = $('.chat-placeholder');
  const sidebar = $('.col-3');
  const hamburgerMenu = $('.hamburger-menu');
  const addChatButton = $('.addchat a');
  const chatList = $('#chat-list');

  let currentConversationId = null;

  // 加載對話列表
  function loadConversations() {
    $.ajax({
      url: '/api/conversations',
      method: 'GET',
      success: function (conversations) {
        chatList.empty();
        conversations.forEach(function (conv) {
          const newChatItem = $('<a>')
            .addClass('list-group-item list-group-item-action d-flex justify-content-between align-items-center')
            .attr({
              href: '#',
              'data-conversation-id': conv.id,
            })
            .html(`<div><i class="bi bi-chat-dots me-2"></i>${conv.name}</div>`);
          const deleteButton = $('<button>')
            .addClass('btn btn-danger btn-sm delete-conversation')
            .text('刪除')
            .attr('data-conversation-id', conv.id);
          newChatItem.append(deleteButton);
          chatList.append(newChatItem);
        });
      },
      error: function (error) {
        console.error('Error loading conversations:', error);
      },
    });
  }

  // 創建新對話並發送消息
  function createNewConversation(message) {
    const conversationName = `新對話${Date.now()}`;
    $.ajax({
      url: '/api/new_conversation',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ name: conversationName }),
      success: function (conversation) {
        // 創建新的對話項目
        const newChatItem = $('<a>')
          .addClass('list-group-item list-group-item-action d-flex justify-content-between align-items-center')
          .attr({
            href: '#',
            'data-conversation-id': conversation.id,
          })
          .html(`<div><i class="bi bi-chat-dots me-2"></i>${conversation.name}</div>`);
        const deleteButton = $('<button>')
          .addClass('btn btn-danger btn-sm delete-conversation')
          .text('刪除')
          .attr('data-conversation-id', conversation.id);
        newChatItem.append(deleteButton);
        chatList.prepend(newChatItem);

        // 切換到新對話
        setActiveChat(newChatItem);

        // 顯示用戶消息
        appendUserMessage(message);
        chatInput.val('');
        scrollToBottom();

        // 發送消息到伺服器
        sendMessageToServer(message, conversation.id);
      },
      error: function (error) {
        console.error('Error creating conversation:', error);
      },
    });
  }

  // 發送消息到伺服器
  function sendMessageToServer(message, conversationId) {
    $.ajax({
      url: '/api/message',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        message: message,
        conversation_id: conversationId,
      }),
      success: function (data) {
        // 顯示 AI 回覆
        appendBotMessage(data.reply);
        scrollToBottom();
      },
      error: function (error) {
        console.error('Error:', error);
      },
    });
  }

  // 設置活躍對話
  function setActiveChat(chatItem) {
    $('.list-group-item').removeClass('active');
    chatItem.addClass('active');

    // 獲取對話ID
    currentConversationId = chatItem.attr('data-conversation-id');

    // 載入對話歷史
    $.ajax({
      url: `/api/chat_history/${currentConversationId}`,
      method: 'GET',
      success: function (messages) {
        chatContent.empty();
        placeholder.hide();

        // 渲染歷史消息
        messages.forEach(function (msg) {
          if (msg.sender === 'user') {
            appendUserMessage(msg.message);
          } else {
            appendBotMessage(msg.message);
          }
        });

        scrollToBottom();
      },
      error: function (error) {
        console.error('Error loading chat history:', error);
      },
    });

    if ($(window).width() < 767) {
      sidebar.removeClass('show');
    }
  }

  // 發送消息
  sendButton.on('click', function () {
    const message = chatInput.val().trim(); // 使用者輸入的問題
    if (message) {
      if (!currentConversationId) {
        placeholder.hide(); //隱藏一開始ntnu logo
        // 如果沒有活躍對話，創建新對話並顯示第一次問題
        $.ajax({
          url: '/api/new_conversation',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({ name: `新對話${Date.now()}` }),
          success: function (conversation) {
            currentConversationId = conversation.id;

            // 創建新的對話項目
            const newChatItem = $('<a>')
              .addClass('list-group-item list-group-item-action d-flex justify-content-between align-items-center active')
              .attr({
                href: '#',
                'data-conversation-id': conversation.id,
              })
              .html(`<div><i class="bi bi-chat-dots me-2"></i>${conversation.name}</div>`);
            const deleteButton = $('<button>')
              .addClass('btn btn-danger btn-sm delete-conversation')
              .text('刪除')
              .attr('data-conversation-id', conversation.id);
            newChatItem.append(deleteButton);
            chatList.prepend(newChatItem);

            // 顯示第一次問題在對話框中
            const messageElement = $('<div>')
              .addClass('d-flex justify-content-end mb-3')
              .html(`<div class="bg-primary text-white p-2 rounded">${message}</div>`);
            chatContent.append(messageElement);
            chatInput.val(''); // 清空輸入框
            scrollToBottom(); // 滾動到底部

            // 發送第一次問題到伺服器
            $.ajax({
              url: '/api/message',
              method: 'POST',
              contentType: 'application/json',
              data: JSON.stringify({
                message: message,
                conversation_id: currentConversationId
              }),
              success: function (data) {
                // 顯示 AI 回覆
                const botMessageElement = $('<div>')
                  .addClass('d-flex justify-content-start mb-3')
                  .html(`<div class="bg-light text-dark p-2 rounded">${data.reply}</div>`);
                chatContent.append(botMessageElement);
                scrollToBottom(); // 滾動到底部
              },
              error: function (error) {
                console.error('Error sending message:', error);
              }
            });
          },
          error: function (error) {
            console.error('Error creating conversation:', error);
          }
        });
      } else {
        // 已有活躍對話，顯示用戶問題並發送到伺服器
        const messageElement = $('<div>')
          .addClass('d-flex justify-content-end mb-3')
          .html(`<div class="bg-primary text-white p-2 rounded">${message}</div>`);
        chatContent.append(messageElement);
        chatInput.val(''); // 清空輸入框
        scrollToBottom(); // 滾動到底部

        // 發送消息到伺服器
        $.ajax({
          url: '/api/message',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({
            message: message,
            conversation_id: currentConversationId
          }),
          success: function (data) {
            // 顯示 AI 回覆
            const botMessageElement = $('<div>')
              .addClass('d-flex justify-content-start mb-3')
              .html(`<div class="bg-light text-dark p-2 rounded">${data.reply}</div>`);
            chatContent.append(botMessageElement);
            scrollToBottom(); // 滾動到底部
          },
          error: function (error) {
            console.error('Error sending message:', error);
          }
        });
      }
    }
  });

  // 新增對話按鈕
  addChatButton.on('click', function () {
    createNewConversation('');
  });

  // 對話列表點擊事件
  chatList.on('click', '.list-group-item', function (event) {
    setActiveChat($(this));
  });

  // 刪除對話按鈕點擊事件
  chatList.on('click', '.delete-conversation', function (event) {
    event.stopPropagation();
    const conversationId = $(this).attr('data-conversation-id');
    $.ajax({
      url: `/api/delete_conversation/${conversationId}`,
      method: 'DELETE',
      success: function () {
        loadConversations();
        // 清空聊天內容
        chatContent.empty();
        // 顯示 placeholder
        placeholder.show();
        // 重置當前對話 ID
        currentConversationId = null;
      },
      error: function (error) {
        console.error('Error deleting conversation:', error);
      }
    });
  });

  // 漢堡菜單
  hamburgerMenu.on('click', function () {
    sidebar.toggleClass('show');
  });

  // 滾動到底部
  function scrollToBottom() {
    chatContent.scrollTop(chatContent[0].scrollHeight);
  }

  // 顯示用戶消息
  function appendUserMessage(message) {
    const messageElement = $('<div>')
      .addClass('d-flex justify-content-end mb-3')
      .html(`<div class="bg-primary text-white p-2 rounded">${message}</div>`);
    chatContent.append(messageElement);
    scrollToBottom(); // 滾動到底部
  }

  // 顯示 AI 回覆
  function appendBotMessage(message) {
    const botMessageElement = $('<div>')
      .addClass('d-flex justify-content-start mb-3')
      .html(`<div class="bg-light text-dark p-2 rounded">${message}</div>`);
    chatContent.append(botMessageElement);
    scrollToBottom(); // 滾動到底部
  }

  // 初始化：載入對話列表
  loadConversations();
});
