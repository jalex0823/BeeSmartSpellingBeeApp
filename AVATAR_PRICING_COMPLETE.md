# 🐝 BeeSmart Spelling Bee - Complete Avatar Unlock & Pricing Guide

**Last Updated:** November 3, 2025  
**App Version:** v2.1  
**Default Locked Avatar Price:** $0.99 USD (unless noted)

---

## 📊 Avatar Unlock System Overview

BeeSmart uses a **3-tier unlock system** for avatars:

1. **FREE (Default Available)** - 6 avatars included with app download
2. **EARN OR BUY** - 7 avatars unlockable with Honey Points OR $0.99 purchase
3. **PREMIUM** - 11 avatars unlockable with high Honey Points; most are $0.99, but the following are $1.99 each (or via bundle): Al Bee, Astro Bee, Biker Bee, Diva Bee, Superbee, Queen Bee, Robo Bee, Ware Bee, Zom Bee

**Total: 24 Bee Avatars** (1 Mascot + 5 Default Free + 7 Earn/Buy + 11 Premium)

---

## 🆓 FREE AVATARS (Always Unlocked)

### Tier: Default Free - 0 Points, Not Purchasable

| Avatar ID | Display Name | Category | Description |
|-----------|--------------|----------|-------------|
| **mascot-bee** | Mascot Bee | Classic | The original BeeSmart mascot! Default for guests. |
| **brother-bee** | Brother Bee | Classic | Your reliable bee bro — friendly and helpful! |
| **builder-bee** | Builder Bee | Profession | Hard hat on! Builds and fixes around the hive. |
| **cool-bee** | Cool Bee | Classic | The coolest bee around - always stylish! |
| **detective-bee** | Detective Bee | Profession | Elementary, my dear Wats-bee! Solving word mysteries. |
| **explorer-bee** | Explorer Bee | Adventure | Adventure awaits! Ready to discover new horizons. |

**Total Free Avatars: 6**  
**Unlock Cost: $0.00** | **Points Required: 0**

---

## 💰 EARN OR BUY AVATARS

### Tier: Earn-or-Buy - Unlock with Points OR $0.99 Purchase

| Avatar ID | Display Name | Points | Price | Category | Description |
|-----------|--------------|--------|-------|----------|-------------|
| **buzz-bee** | Buzz Bee | 3,000 | $0.99 | Classic | Always buzzing with energy and enthusiasm! |
| **doctor-bee** | Doctor Bee | 2,000 | $0.99 | Profession | Here to heal and help! Medical professional bee. |
| **knight-bee** | Knight Bee | 4,000 | $0.99 | Fantasy | Brave and noble! Defender of the hive. |
| **monster-bee** | Monster Bee | 6,000 | $0.99 | Fantasy | Not scary, just misunderstood! Friendly monster. |
| **rocker-bee** | Rocker Bee | 8,000 | $0.99 | Entertainment | Rock and roll! Lead singer of The Bee-tles. |
| **selfie-bee** | Selfie Bee | 5,000 | $0.99 | Entertainment | Say cheese! Always ready for the perfect selfie! |
| **seabea** | Seabea | 10,000 | $0.99 | Adventure | Navy SeaBee! Construction battalion of the ocean. |

**Total Earn/Buy Avatars: 7**  
**Points Range: 2,000 - 10,000** | **Purchase Price: $0.99 each**

---

## 👑 PREMIUM AVATARS

### Tier: Premium - High Points; $0.99 default, $1.99 for highlighted set

| Avatar ID | Display Name | Points | Price | Category | Description |
|-----------|--------------|--------|-------|----------|-------------|
| **diva-bee** | Diva Bee | 12,000 | $1.99 | Entertainment | The Bee-yoncé of the hive! Born to spell, born to shine! |
| **biker-bee** | Biker Bee | 15,000 | $1.99 | Action | Born to Bee Wild! Rides a Harley-Davidson Honey-Hog. |
| **astro-bee** | Astro Bee | 18,000 | $1.99 | Adventure | Buzz Aldrin's cousin! First bee on the moon. |
| **al-bee** | Al Bee | 20,000 | $1.99 | Classic | Genius bee! Discovered E=MC² (Mighty Cool Buzzing²) |
| **professor-bee** | Professor Bee | 22,000 | $0.99 | Profession | Wise and knowledgeable! The scholarly bee. |
| **vamp-bee** | Vamp Bee | 24,000 | $0.99 | Fantasy | Count Bee-cula! 'I vant to spell your vords!' |
| **franken-bee** | Franken Bee | 25,000 | $0.99 | Fantasy | Created by Dr. Franken-sting! Spells by lightning. |
| **zom-bee** | Zom Bee | 25,000 | $1.99 | Fantasy | The Walking Buzzed! Craves brainy words. |
| **superbee** | Superbee | 26,000 | $1.99 | Fantasy | Saving the day with bee powers! Cape included. |
| **ware-bee** | Ware Bee | 27,000 | $1.99 | Fantasy | Were-bee of London! Howls at the full moon. |
| **queen-bee** | Queen Bee | 28,000 | $1.99 | Royal | Royal and majestic! Leader with grace. |
| **robo-bee** | Robo Bee | 30,000 | $1.99 | Tech | Buzzbot 3000! Honey-powered circuits. |

**Total Premium Avatars: 12**  
**Points Range: 12,000 - 30,000** | **Purchase Price: $0.99 each**

---

## 🎁 SPECIAL AVATARS

### Tier: Special - Unique Unlock Requirements

| Avatar ID | Display Name | Points | Price | Category | Description |
|-----------|--------------|--------|-------|----------|-------------|
| **anxious-bee** | Anxious Bee | 5,000 | $0.99 | Emotion | A little nervous but eager to learn! |

**Total Special Avatars: 1**  
**Purchase Price: $0.99**

---

## 📱 Mobile App Configuration

### For App Developers - JSON Config Format (reflects $1.99 premium set)

```json
{
  "avatar_pricing": {
    "default_locked_price": 0.99,
    "currency": "USD",
    "free_avatars": ["mascot-bee", "brother-bee", "builder-bee", "cool-bee", "detective-bee", "explorer-bee"],
    "earn_or_buy": {
      "buzz-bee": {"points": 3000, "price": 0.99},
      "doctor-bee": {"points": 2000, "price": 0.99},
      "knight-bee": {"points": 4000, "price": 0.99},
      "monster-bee": {"points": 6000, "price": 0.99},
      "rocker-bee": {"points": 8000, "price": 0.99},
      "selfie-bee": {"points": 5000, "price": 0.99},
      "seabea": {"points": 10000, "price": 0.99}
    },
    "premium": {
  "diva-bee": {"points": 12000, "price": 1.99},
  "biker-bee": {"points": 15000, "price": 1.99},
  "astro-bee": {"points": 18000, "price": 1.99},
  "al-bee": {"points": 20000, "price": 1.99},
  "professor-bee": {"points": 22000, "price": 0.99},
  "vamp-bee": {"points": 24000, "price": 0.99},
  "franken-bee": {"points": 25000, "price": 0.99},
  "zom-bee": {"points": 25000, "price": 1.99},
  "superbee": {"points": 26000, "price": 1.99},
  "ware-bee": {"points": 27000, "price": 1.99},
  "queen-bee": {"points": 28000, "price": 1.99},
  "robo-bee": {"points": 30000, "price": 1.99}
    },
    "special": {
      "anxious-bee": {"points": 5000, "price": 0.99}
    }
  }
}
```

---

## 💳 In-App Purchase Implementation

### Purchase Flow
1. User views locked avatar in honeycomb picker
2. Shows "🔒 Unlock for $0.99 or 5,000 🍯"
3. Tap avatar → Modal with unlock options:
   - **Button 1:** "Unlock with 5,000 Honey Points" (if available)
   - **Button 2:** "Purchase for $0.99"
4. Process payment via App Store / Google Play
5. Unlock avatar immediately
6. Save purchase to user account (cross-device sync)

### Purchase SKU Format
- `com.beesmart.avatar.[avatar-id]`
- Example: `com.beesmart.avatar.queen-bee`

---

## 🍯 Honey Points Earning System

### How to Earn Points

| Activity | Points Earned |
|----------|---------------|
| **Correct Answer (First Try)** | 100 points |
| **Correct Answer (Second Try)** | 50 points |
| **Correct Answer (Third Try+)** | 25 points |
| **Speed Bonus (< 5 seconds)** | +25 points |
| **No Hint Used** | +25 points |
| **Perfect Streak (10+)** | +100 bonus |

### Badge Bonuses

| Badge Achievement | Bonus Points |
|-------------------|--------------|
| 🌟 **Perfect Game** | +500 |
| ⚡ **Speed Demon** | +200 |
| 📚 **Persistent Learner** | +150 |
| 🔥 **Hot Streak** | +100 |
| 🎯 **Comeback Kid** | +100 |
| 🍯 **Honey Hunter** | +75 |
| 🐝 **Early Bird** | +50 |

---

## 🎯 Avatar Unlock Strategy Guide

### Fastest Path to Premium Avatars

1. **Start with Free Avatars** (0 points)
   - Use Mascot Bee as guest
   - Register to access 5 more free avatars

2. **Early Unlocks (2,000-6,000 points)**
   - Doctor Bee (2,000) - Easiest first unlock
   - Buzz Bee (3,000) - Popular choice
   - Knight Bee (4,000) - Fan favorite
   - Monster Bee (6,000) - Worth the grind

3. **Mid-Tier Goals (8,000-12,000 points)**
   - Rocker Bee (8,000) - Rock star vibes
   - Seabea (10,000) - Military pride
   - Diva Bee (12,000) - First premium unlock

4. **Premium Targets (15,000-30,000 points)**
   - Focus on favorite character
   - Or purchase for $0.99 each

### Purchase vs. Earn Decision

**When to Purchase ($0.99):**
- Want avatar immediately
- Don't have time to earn points
- Special occasion / gift
- Supporting app development

**When to Earn (Honey Points):**
- Enjoy the challenge
- Teaching kids patience / rewards
- Free method preferred
- Have time to practice spelling

---

## 🛡️ Admin Override & Special Access

### Admin Users (Role: admin)
- **Bypass all locks** - All avatars instantly available
- No points or purchase required
- Used for testing and demonstrations

### Teacher/Parent Accounts
- Can **gift avatars** to linked students
- View student avatar collections
- Track unlock progress

---

## 📈 Analytics & Metrics

### Conversion Tracking

| Metric | Target | Purpose |
|--------|--------|---------|
| **Free-to-Paid Conversion** | 15-20% | Users who purchase any avatar |
| **Average Revenue Per User (ARPU)** | $2-3 | Based on $0.99 pricing |
| **Points-to-Purchase Ratio** | 60/40 | 60% earn, 40% purchase |
| **Most Popular Purchases** | Top 5 | Optimize marketing |

### User Behavior Insights
- Track which avatars are **most frequently purchased**
- Identify **optimal point thresholds** (not too easy/hard)
- Monitor **purchase timing** (new users vs. veterans)
- A/B test **pricing variations** (seasonal sales)

---

## 🔄 Version History

### v2.1 - Current (Nov 3, 2025)
- ✅ Default locked price is $0.99; select premium avatars at $1.99 (Al, Astro, Biker, Diva, Superbee, Queen, Robo, Ware, Zom Bee)
- ✅ Consistent monetization across website and mobile app
- ✅ Thumbnail validation system implemented

### v2.0 - Previous
- Variable pricing ($0.99 - $2.99) based on rarity
- Premium avatars priced at $1.99-$2.99

---

## 📞 Support & Questions

For pricing inquiries or purchase issues:
- **Email:** support@beesmartspelling.app
- **In-App:** Settings → Help & Support
- **Website:** https://beesmartspelling.app/help

---

**🐝 Happy Spelling! May your Honey Points flow like nectar! 🍯**
