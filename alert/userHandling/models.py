# This software and any associated files are copyright 2010 Brian Carver and
# Michael Lissner.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.models import USStateField
from django.core.validators import MaxLengthValidator
from alert.alertSystem.models import Document

FREQUENCY = (
    ('dly', 'Daily'),
    ('wly', 'Weekly'),
    ('mly', 'Monthly'),
    ('off', 'Off'),
)


# a class where alerts are held/handled.
class Alert(models.Model):
    alertUUID = models.AutoField('a unique ID for each alert', primary_key=True)
    alertName = models.CharField('a name for the alert', max_length=75)
    alertText = models.CharField('the text of an alert created by a user',
        max_length=200)
    alertFrequency = models.CharField('the rate chosen by the user for the alert',
        choices=FREQUENCY,
        max_length=10)
    alertPrivacy = models.BooleanField('should the alert be considered private',
        default=True)
    sendNegativeAlert = models.BooleanField('should alerts be sent when there are no hits during a specified period',
        default=False)
    lastHitDate = models.DateTimeField('the exact date and time stamp that the alert last sent an email',
        blank=True,
        null=True)

    def __unicode__(self):
        return 'Alert ' + str(self.alertUUID) + ': ' + self.alertText

    class Meta:
        verbose_name = 'alert'
        ordering = [ 'alertFrequency', 'alertText']
        db_table = 'Alert'


# a class where favorites are held
class Favorite(models.Model):
    doc_id = models.ForeignKey(Document,
        verbose_name='the document that is favorited')
    name  = models.CharField('a name for the alert', max_length=100)
    notes = models.TextField('notes about the favorite',
        validators=[MaxLengthValidator(500)],
        max_length=500,
        blank=True)
    def __unicode__(self):
        return 'Favorite %s' % self.id

    class Meta:
        db_table = 'Favorite'


# a class where bar memberships are held and handled.
class BarMembership(models.Model):
    barMembershipUUID = models.AutoField('a unique ID for each bar membership',
        primary_key=True)
    barMembership = USStateField('the two letter state abbreviation of a bar membership')

    def __unicode__(self):
        return self.get_barMembership_display()

    class Meta:
        verbose_name = 'bar membership'
        db_table = 'BarMembership'
        ordering = ['barMembership']


# a class to extend the User class with the fields we need.
class UserProfile(models.Model):
    userProfileUUID = models.AutoField('a unique ID for each user profile',
        primary_key=True)
    user = models.ForeignKey(User,
        verbose_name='the user this model extends',
        unique=True)
    location = models.CharField('the location of the user',
        max_length=100,
        blank=True)
    employer = models.CharField('the user\'s employer',
        max_length=100,
        blank=True)
    avatar = models.ImageField('the user\'s avatar',
        upload_to='avatars/%Y/%m/%d',
        blank=True)
    wantsNewsletter = models.BooleanField('does the user want newsletters',
        default=False)
    barmembership = models.ManyToManyField(BarMembership,
        verbose_name='the bar memberships held by the user',
        blank=True,
        null=True)
    alert = models.ManyToManyField(Alert,
        verbose_name='the alerts created by the user',
        blank=True,
        null=True)
    favorite = models.ManyToManyField(Favorite,
        verbose_name = 'the favorites created by the user',
        related_name = 'users',
        blank=True,
        null=True)
    plaintextPreferred = models.BooleanField('should the alert should be sent in plaintext',
        default=False)
    activationKey = models.CharField(max_length=40)
    key_expires = models.DateTimeField('The time and date when the user\'s activationKey expires',
        blank=True,
        null=True)
    emailConfirmed = models.BooleanField('The user has confirmed their email address',
        default=False)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'
        db_table = 'UserProfile'
