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
          const newChatItem = createChatListItem(conv);
          chatList.append(newChatItem);
        });
      },
      error: function (error) {
        console.error('Error loading conversations:', error);
      },
    });
  }

  // 創建聊天列表項目
  function createChatListItem(conversation) {
    const chatName = $('<div>')
      .addClass('chat-name')
      .html(`<i class="bi bi-chat-dots me-2"></i>${conversation.name}`);
      
    const input = $('<input>')
      .addClass('form-control d-none')
      .val(conversation.name);
      
    const nameContainer = $('<div>')
      .addClass('d-flex justify-content-between align-items-center w-100')
      .append(chatName)
      .append(input);
    
    const buttonContainer = $('<div>')
    .addClass('d-flex buttongroup');

    const editButton = $('<button>')
    .addClass('btn btn-primary btn-sm edit-conversation')
    .text('編輯')
    .attr('data-conversation-id', conversation.id);

    const deleteButton = $('<button>')
    .addClass('btn btn-danger btn-sm delete-conversation')
    .text('刪除')
    .attr('data-conversation-id', conversation.id);

    buttonContainer.append(editButton).append(deleteButton);
      
    return $('<a>')
      .addClass('list-group-item list-group-item-action d-flex justify-content-between align-items-center')
      .attr({
        'href': '#',
        'data-conversation-id': conversation.id
      })
      .append(nameContainer)
      .append(buttonContainer);
      
  }

  // 創建新對話並發送消息
  function createNewConversation(message) {
    const conversationName = message ? message.substring(0, 20) : `新對話${Date.now()}`;
    $.ajax({
      url: '/api/new_conversation',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({ name: conversationName }),
      success: function(conversation) {
        const newChatItem = createChatListItem(conversation);
        chatList.prepend(newChatItem);
        setActiveChat(newChatItem);
        
        if (message) {
          appendUserMessage(message);
          chatInput.val('');
          scrollToBottom();
          sendMessageToServer(message, conversation.id);
        }
      },
      error: function(error) {
        console.error('Error creating conversation:', error);
      }
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
    currentConversationId = chatItem.attr('data-conversation-id');

    $.ajax({
      url: `/api/chat_history/${currentConversationId}`,
      method: 'GET',
      success: function (messages) {
        chatContent.empty();
        placeholder.hide();

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
        data: JSON.stringify({ name: message.substring(0, 20) }), // 使用消息前20個字符作為名稱
        success: function (conversation) {
          currentConversationId = conversation.id;

          // 創建新的對話項目
          const chatName = $('<div>')
            .addClass('chat-name')
            .html(`<i class="bi bi-chat-dots me-2"></i>${conversation.name}`);
            
          const input = $('<input>')
            .addClass('form-control d-none')
            .val(conversation.name);
            
          const nameContainer = $('<div>')
            .append(chatName)
            .append(input);

          const buttonContainer = $('<div>')
          .addClass('d-flex');  
                    
          const editButton = $('<button>')
          .addClass('btn btn-primary btn-sm edit-conversation')
          .text('編輯')
          .attr('data-conversation-id', conversation.id);  

          const deleteButton = $('<button>')
          .addClass('btn btn-danger btn-sm delete-conversation')
          .text('刪除')
          .attr('data-conversation-id', conversation.id);
          
          buttonContainer.append(editButton).append(deleteButton);

          const newChatItem = $('<a>')
            .addClass('list-group-item list-group-item-action d-flex justify-content-between align-items-center active')
            .attr({
              href: '#',
              'data-conversation-id': conversation.id,
            })
            .append(nameContainer)
            .append(buttonContainer);
            
            
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


  //改左邊聊天室名稱
  // 編輯左邊新對話聊天室按鈕點擊事件
  chatList.on('click', '.edit-conversation', function(event) {
  event.stopPropagation();
  const chatItem = $(this).closest('.list-group-item');
  const nameContainer = chatItem.find('.chat-name').parent();
  const chatName = nameContainer.find('.chat-name');
  const input = nameContainer.find('input');
  
  // 顯示輸入框並隱藏原本的名稱
  chatName.addClass('d-none');
  input.removeClass('d-none')
    .val(chatName.text().trim())  // 設置當前名稱為輸入框的值
    .focus();
});

  // 雙擊編輯對話名稱
  chatList.on('dblclick', '.chat-name', function(e) {
    e.preventDefault();
    const nameContainer = $(this).parent();
    const chatName = $(this);
    const input = nameContainer.find('input');
    
    chatName.addClass('d-none');
    input.removeClass('d-none').focus();
  });


  // 當輸入框失去焦點時儲存
  chatList.on('blur', 'input', function() {
    const input = $(this);
    const chatItem = input.closest('.list-group-item');
    const nameContainer = input.parent();
    const chatName = nameContainer.find('.chat-name');
    const newName = input.val().trim();
    const conversationId = chatItem.attr('data-conversation-id');
    
    if (newName) {
      $.ajax({
        url: `/api/rename_conversation/${conversationId}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({ name: newName }),
        success: function(response) {
          // 更新顯示的名稱，保持圖示
          chatName.html(`<i class="bi bi-chat-dots me-2"></i>${newName}`);
          // 切換顯示狀態
          input.addClass('d-none');
          chatName.removeClass('d-none');
        },
        error: function(error) {
          console.error('編輯對話名稱時發生錯誤:', error);
          alert('編輯失敗，請稍後再試');
          // 發生錯誤時恢復原本的名稱
          input.addClass('d-none');
          chatName.removeClass('d-none');
        }
      });
    }
  });

  // 按下 Enter 鍵時也要儲存
  chatList.on('keypress', 'input', function(e) {
    if (e.which === 13) {
      $(this).blur();
    }
  });

  //搜尋聊天室關鍵字
  // 全域搜索功能
  $('#button-addon2').on('click', function() {
    const searchText = $('input[placeholder="搜尋..."]').val().toLowerCase().trim();
    performSearch(searchText);
  });

  // 搜尋輸入框的 Enter 鍵事件
  $('input[placeholder="搜尋..."]').on('keypress', function(e) {
    if (e.which === 13) {
      const searchText = $(this).val().toLowerCase().trim();
      performSearch(searchText);
    }
  });

  // 執行搜尋的函數
  function performSearch(searchText) {
    if (!searchText) {
      // 如果搜尋文字為空，顯示所有對話
      $('#chat-list .list-group-item').show();
      $('.chat-content div').show();
      return;
    }

    // 搜尋左側對話列表
    $('#chat-list .list-group-item').each(function() {
      const chatName = $(this).find('.chat-name').text().toLowerCase();
      $(this).toggle(chatName.includes(searchText));
    });

    // 全域搜尋所有聊天記錄
    $.ajax({
      url: '/api/search_messages',
      method: 'GET',
      data: { 
        query: searchText 
      },
      success: function(results) {
        // 清空當前聊天內容
        $('.chat-content').empty();
        $('.chat-placeholder').hide();

        if (results.length === 0) {
          $('.chat-content').append(
            $('<div>').addClass('text-center text-muted mt-3')
              .text('找不到符合的訊息')
          );
          return;
        }

        // 顯示搜尋結果
        results.forEach(function(result) {
          const messageElement = $('<div>')
            .addClass('search-result mb-3')
            .append(
              $('<div>').addClass('text-muted small mb-1')
                .text(`來自對話: ${result.conversation_name}`)
            );

          // 根據發送者設置不同的樣式
          const messageContent = $('<div>')
            .addClass('p-2 rounded')
            .text(result.message);

          if (result.sender === 'user') {
            messageContent.addClass('bg-primary text-white');
            messageElement.addClass('d-flex justify-content-end');
          } else {
            messageContent.addClass('bg-light text-dark');
            messageElement.addClass('d-flex justify-content-start');
          }

          messageElement.append(messageContent);
          $('.chat-content').append(messageElement);
        });
      },
      error: function(error) {
        console.error('搜尋時發生錯誤:', error);
        $('.chat-content').append(
          $('<div>').addClass('text-center text-danger mt-3')
            .text('搜尋時發生錯誤，請稍後再試')
        );
      }
    });
  }


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
