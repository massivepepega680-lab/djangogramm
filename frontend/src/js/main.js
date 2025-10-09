import '../scss/main.scss';
import 'bootstrap';
import 'jquery';
import 'popper.js';
import Vue from 'vue';
import LikeButton from './components/LikeButton.vue';
import FollowButton from './components/FollowButton.vue';
import { initThemeToggle } from './theme-toggle';

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
});

const apps = document.querySelectorAll('.vue-app');
if (apps.length > 0) {
  new Vue({
    el: '.vue-app',
    components: {
      LikeButton,
      FollowButton
    },
    methods: {
      updateFollowerCount(newCount) {
        console.log('Event received! New follower count:', newCount); // For debugging
        const followerCountElement = document.getElementById('follower-count');
        if (followerCountElement) {
            followerCountElement.innerText = newCount;
        }
      }
    }
  });
}