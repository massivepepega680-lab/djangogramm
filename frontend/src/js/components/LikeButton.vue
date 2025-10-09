<template>
  <div>
    <button @click="toggleLike" :class="buttonClass">
      {{ likeCount }} {{ buttonText }}
    </button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    postId: {
      type: Number,
      required: true
    },
    initialLikes: {
      type: Number,
      required: true
    },
    isInitiallyLiked: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      likeCount: this.initialLikes,
      isLiked: this.isInitiallyLiked,
      isLoading: false
    }
  },
  computed: {
    buttonText() {
      return this.likeCount === 1 ? 'Like' : 'Likes';
    },
    buttonClass() {
      return this.isLiked ? 'btn btn-primary' : 'btn btn-outline-primary';
    }
  },
  methods: {
    toggleLike() {
      if (this.isLoading) return;
      this.isLoading = true;

      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      axios.post(`/posts/post/${this.postId}/toggle_like/`, {}, {
        headers: {'X-CSRFToken': csrfToken}
      })
      .then(response => {
        this.isLiked = response.data.is_liked;
        this.likeCount = response.data.like_count;
      })
      .catch(error => {
        console.error("There was an error liking the post:", error);
        if (error.response && error.response.status === 403) {
            window.location.href = '/users/login/';
        }
      })
      .finally(() => {
        this.isLoading = false;
      });
    }
  }
}
</script>